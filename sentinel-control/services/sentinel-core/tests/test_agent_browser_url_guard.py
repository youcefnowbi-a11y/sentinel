from __future__ import annotations

from sentinel.agent.browser import PublicUrlDecisionStatus, PublicUrlGuard, PublicUrlPolicy


class FakeResolver:
    def __init__(self, mapping: dict[str, list[str]] | None = None, *, fail: bool = False):
        self.mapping = mapping or {}
        self.fail = fail
        self.calls: list[str] = []

    def __call__(self, host: str) -> list[str]:
        self.calls.append(host)
        if self.fail:
            raise RuntimeError("fake resolver failure")
        return self.mapping.get(host, [])


def test_public_url_guard_allows_https_public_url_with_fake_dns():
    resolver = FakeResolver({"example.com": ["93.184.216.34"]})

    decision = PublicUrlGuard().evaluate("https://Example.COM/path#fragment", resolver=resolver)

    assert decision.status == PublicUrlDecisionStatus.ALLOWED
    assert decision.allowed is True
    assert decision.reason == "allowed_public_url"
    assert decision.host == "example.com"
    assert decision.normalized_url == "https://example.com/path"
    assert decision.final_url == "https://example.com/path"
    assert decision.resolved_addresses == ["93.184.216.34"]
    assert resolver.calls == ["example.com"]


def test_public_url_guard_blocks_http_by_default():
    decision = PublicUrlGuard().evaluate("http://example.com", resolver=FakeResolver({"example.com": ["93.184.216.34"]}))

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "unsupported_scheme"


def test_public_url_guard_can_allow_http_when_policy_explicitly_allows_it():
    policy = PublicUrlPolicy(allowed_schemes=["https", "http"])
    decision = PublicUrlGuard().evaluate("http://example.com", policy=policy, resolver=FakeResolver({"example.com": ["93.184.216.34"]}))

    assert decision.status == PublicUrlDecisionStatus.ALLOWED


def test_public_url_guard_blocks_missing_scheme_and_file_scheme():
    guard = PublicUrlGuard()

    missing_scheme = guard.evaluate("example.com", resolver=FakeResolver())
    file_url = guard.evaluate("file:///etc/passwd", resolver=FakeResolver())

    assert missing_scheme.reason == "invalid_url"
    assert file_url.reason == "unsupported_scheme"


def test_public_url_guard_blocks_localhost_without_dns_lookup():
    resolver = FakeResolver({"localhost": ["93.184.216.34"]})

    decision = PublicUrlGuard().evaluate("https://localhost", resolver=resolver)

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "blocked_hostname"
    assert resolver.calls == []


def test_public_url_guard_blocks_private_and_mapped_loopback_ip_literals():
    guard = PublicUrlGuard()

    assert guard.evaluate("https://127.0.0.1").reason == "private_or_internal_ip"
    assert guard.evaluate("https://10.0.0.1").reason == "private_or_internal_ip"
    assert guard.evaluate("https://169.254.169.254").reason == "private_or_internal_ip"
    assert guard.evaluate("https://[::1]").reason == "private_or_internal_ip"
    assert guard.evaluate("https://[::ffff:127.0.0.1]").reason == "private_or_internal_ip"


def test_public_url_guard_blocks_obfuscated_ip_literals():
    guard = PublicUrlGuard()
    resolver = FakeResolver({"2130706433": ["93.184.216.34"], "0x7f000001": ["93.184.216.34"]})

    assert guard.evaluate("https://2130706433", resolver=resolver).reason == "obfuscated_ip_literal_not_allowed"
    assert guard.evaluate("https://0x7f000001", resolver=resolver).reason == "obfuscated_ip_literal_not_allowed"
    assert guard.evaluate("https://0177.0.0.1", resolver=resolver).reason == "obfuscated_ip_literal_not_allowed"
    assert resolver.calls == []


def test_public_url_guard_blocks_raw_control_characters():
    guard = PublicUrlGuard()

    decision = guard.evaluate("https://example.com\r\nHost: internal", resolver=FakeResolver({"example.com": ["93.184.216.34"]}))

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "unsafe_url_characters"


def test_public_url_guard_blocks_metadata_and_internal_hosts():
    guard = PublicUrlGuard()

    assert guard.evaluate("https://metadata.google.internal", resolver=FakeResolver()).reason == "blocked_hostname"
    assert guard.evaluate("https://service.internal", resolver=FakeResolver()).reason == "blocked_hostname"
    assert guard.evaluate("https://printer.local", resolver=FakeResolver()).reason == "blocked_hostname"


def test_public_url_guard_blocks_public_hostname_without_required_resolver():
    decision = PublicUrlGuard().evaluate("https://example.com")

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "dns_resolution_required"


def test_public_url_guard_blocks_dns_failures_and_empty_results():
    guard = PublicUrlGuard()

    failed = guard.evaluate("https://example.com", resolver=FakeResolver(fail=True))
    empty = guard.evaluate("https://example.com", resolver=FakeResolver({}))

    assert failed.reason == "dns_resolution_failed"
    assert empty.reason == "dns_resolution_empty"


def test_public_url_guard_blocks_dns_resolution_to_private_address():
    decision = PublicUrlGuard().evaluate("https://example.com", resolver=FakeResolver({"example.com": ["10.0.0.2"]}))

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "dns_resolution_private_or_internal"


def test_public_url_guard_revalidates_redirects_and_blocks_private_destination():
    resolver = FakeResolver({"example.com": ["93.184.216.34"]})

    decision = PublicUrlGuard().evaluate("https://example.com", resolver=resolver, redirects=["https://127.0.0.1/admin"])

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "private_or_internal_ip"
    assert decision.redirect_chain == ["https://example.com/", "https://127.0.0.1/admin"]


def test_public_url_guard_detects_redirect_loops():
    resolver = FakeResolver({"example.com": ["93.184.216.34"]})

    decision = PublicUrlGuard().evaluate("https://example.com/a", resolver=resolver, redirects=["/b", "/a"])

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "redirect_loop_detected"


def test_public_url_guard_blocks_too_many_redirects_before_dns():
    policy = PublicUrlPolicy(max_redirects=1)
    resolver = FakeResolver({"example.com": ["93.184.216.34"]})

    decision = PublicUrlGuard().evaluate("https://example.com", policy=policy, resolver=resolver, redirects=["/a", "/b"])

    assert decision.status == PublicUrlDecisionStatus.BLOCKED
    assert decision.reason == "too_many_redirects"
    assert resolver.calls == []


def test_public_url_guard_enforces_allowed_domains():
    policy = PublicUrlPolicy(allowed_domains=["example.com"])
    resolver = FakeResolver({"www.example.com": ["93.184.216.34"], "other.com": ["93.184.216.34"]})

    allowed = PublicUrlGuard().evaluate("https://www.example.com/page", policy=policy, resolver=resolver)
    denied = PublicUrlGuard().evaluate("https://other.com/page", policy=policy, resolver=resolver)

    assert allowed.status == PublicUrlDecisionStatus.ALLOWED
    assert denied.status == PublicUrlDecisionStatus.UNAVAILABLE
    assert denied.reason == "domain_not_allowed"
    assert resolver.calls == ["www.example.com"]


def test_public_url_guard_blocks_userinfo_and_invalid_port():
    guard = PublicUrlGuard()

    userinfo = guard.evaluate("https://user:pass@example.com", resolver=FakeResolver({"example.com": ["93.184.216.34"]}))
    invalid_port = guard.evaluate("https://example.com:notaport", resolver=FakeResolver({"example.com": ["93.184.216.34"]}))

    assert userinfo.reason == "userinfo_not_allowed"
    assert invalid_port.reason == "invalid_port"
