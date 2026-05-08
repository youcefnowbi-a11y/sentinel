# P3C OpenClaw Port Map

Date: 2026-04-28
Status: implemented and validated
Scope: Browser guard hardening only

This is a harvest-lab record. It is not product documentation and must not be
copied into `sentinel-control` product docs, runtime logs, tool ids, or user
facing artifacts.

## License And Copy Boundary

The local source snapshot at `agent-lab/vendors/openclaw/source/` carries an MIT
license. For P3C, Sentinel did not import the vendor browser runtime, package
names, gateway/server lifecycle, or TypeScript source. The implementation is a
Sentinel-native Python rewrite informed by the inspected algorithms, failure
modes, and tests.

## Source Files Inspected

| Source file | Harvest purpose |
| --- | --- |
| `src/infra/net/ssrf.ts` | Host normalization, private/internal IP checks, DNS result rejection, pinned lookup/dispatcher concept. |
| `src/infra/net/fetch-guard.ts` | Manual redirect loop with per-hop validation and bounded redirect count. |
| `src/agents/tools/web-fetch.ssrf.test.ts` | Regression cases for private IP literals, private DNS, redirects into private hosts, and public-host allowance. |
| `src/infra/net/ssrf.pinning.test.ts` | Pinning tests and expected behavior for private DNS rejection. |
| `src/infra/fetch.test.ts` | Fetch wrapper patterns; no direct P3C logic ported. |

## Port Decisions

| Extracted primitive | Sentinel destination | Decision | Reason | Tests adapted |
| --- | --- | --- | --- | --- |
| Reject private/internal hostnames and IPs | `sentinel/agent/browser/url_guard.py` | already present | Browser V1 already blocked these classes before fetch. | Existing URL/evidence adapter tests retained. |
| Reject DNS answers that resolve to private/internal addresses | `sentinel/agent/browser/url_guard.py` | already present, regression added | Needed explicit browser adapter coverage, not only URL guard behavior. | `test_browser_evidence_adapter_blocks_private_dns_resolution_before_fetch` |
| Per-hop redirect revalidation | `sentinel/agent/browser/evidence_adapter.py` | translated/rewrite | P3C now follows only response redirects returned by the injected read-only fetcher and re-runs `PublicUrlGuard` before the next fetch. | `test_browser_evidence_adapter_blocks_redirect_to_private_host_before_second_fetch`, live redirect test |
| Redirect loop detection | `sentinel/agent/browser/url_guard.py` + adapter redirect loop | translated/rewrite | Guard already modeled redirect chains; adapter now feeds live redirect locations into that guard. | `test_browser_evidence_adapter_blocks_redirect_loop` |
| Max redirect count | `sentinel/agent/browser/evidence_adapter.py` + `PublicUrlPolicy` | translated/rewrite | Adapter now converts live redirect responses into bounded URL policy decisions. | `test_browser_evidence_adapter_blocks_too_many_redirects` |
| DNS pinning concept | `sentinel/agent/browser/models.py`, `evidence_adapter.py`, `live_fetch.py` | Sentinel-native rewrite | P3C adds `BrowserConnectionProof`, optional proof enforcement, and a Python pinned HTTP/HTTPS path that connects to an approved resolved address while preserving the original Host/SNI. It does not import the vendor dispatcher/runtime. | `test_browser_evidence_adapter_accepts_required_connection_proof`, `test_browser_evidence_adapter_rejects_unapproved_connection_proof`, `test_read_only_http_fetcher_pinned_http_path_returns_connection_proof` |
| MIME gate | `sentinel/agent/browser/models.py`, `evidence_adapter.py`, `live_fetch.py` | Sentinel-native addition | The source guard focused SSRF/redirect boundaries. Sentinel added MIME allowlist as a Browser V1 evidence gate. | `test_browser_evidence_adapter_rejects_disallowed_mime_type` |
| Compressed/uncompressed size accounting | `sentinel/agent/browser/models.py`, `evidence_adapter.py`, `live_fetch.py` | Sentinel-native addition | P3C now accounts for compressed raw bytes and decoded body bytes separately before artifact creation. | `test_browser_evidence_adapter_rejects_oversized_compressed_body_without_artifact`, live compressed-size test |
| Full vendor pinned dispatcher | none | reject for P3C | It is coupled to the Node/Undici runtime. Sentinel needs a Python transport-specific implementation later, behind the same proof contract. | Not ported |
| Vendor web tool/gateway runtime | none | reject | Browser V1 stays MissionAuthority/RiskRouter/EventBus governed. Vendor lifecycle is not imported. | Not ported |

## Sentinel Files Changed

| File | Change |
| --- | --- |
| `sentinel-control/services/sentinel-core/sentinel/agent/browser/models.py` | Added MIME allowlist, compressed-size budget, optional connection-proof requirement, `BrowserConnectionProof`, receipt byte/proof fields. |
| `sentinel-control/services/sentinel-core/sentinel/agent/browser/evidence_adapter.py` | Added live redirect loop, per-hop URL classification, MIME gate, compressed/uncompressed byte gates, optional connection-proof validation. |
| `sentinel-control/services/sentinel-core/sentinel/agent/browser/live_fetch.py` | Added raw-body size read, gzip/deflate decode accounting, non-following fetch with redirect headers returned to the adapter. |
| `sentinel-control/services/sentinel-core/tests/test_agent_browser_evidence_adapter.py` | Added hostile URL, redirect, MIME, compressed-size, and proof regression tests. |
| `sentinel-control/services/sentinel-core/tests/test_agent_browser_live_fetch.py` | Updated redirect behavior and added compressed body regression. |

## Rejected For P3C

The following browser powers remain out of scope:

```text
profile/session import
cookies
storage
arbitrary JavaScript
click/type/submit
downloads
external scraper fallback
vendor gateway/server import
```

## Remaining Gap

P3C implements a pinned path for the default `ReadOnlyHttpFetcher` when no
custom transport is injected. Mock/custom transports still rely on their own
connection semantics, so missions that require socket-level proof must set
`require_connection_proof=True` and use the pinned fetcher path.

The next hardening step, if required before broad internet use, is:

```text
PublicUrlDecision.resolved_addresses
-> Python pinned transport stress tests for HTTPS/CDN edge cases
-> connected remote address proof
-> BrowserConnectionProof(pinned=True)
-> receipt/final gate validation
```
