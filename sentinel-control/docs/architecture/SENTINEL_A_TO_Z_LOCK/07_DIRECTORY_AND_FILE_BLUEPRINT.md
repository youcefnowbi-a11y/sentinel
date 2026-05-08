# Directory And File Blueprint

## Organ Foundation

```text
sentinel-control/services/sentinel-core/sentinel/organs/
  __init__.py
  contracts.py
  registry.py
  authority.py
  risk.py
  dry_run.py
  receipts.py
  replay.py
  kill_switch.py
  promotion_gate.py
  vendor_harvest.py
```

## Future Organs

```text
sentinel-control/services/sentinel-core/sentinel/organs/browser/
sentinel-control/services/sentinel-core/sentinel/organs/external_api/
sentinel-control/services/sentinel-core/sentinel/organs/channels/
sentinel-control/services/sentinel-core/sentinel/organs/account_ops/
sentinel-control/services/sentinel-core/sentinel/organs/capital_operator/
sentinel-control/services/sentinel-core/sentinel/organs/trading/
sentinel-control/services/sentinel-core/sentinel/organs/desktop_sidecar/
sentinel-control/services/sentinel-core/sentinel/organs/shell_sandbox/
```

## Finance

```text
sentinel-control/services/sentinel-core/sentinel/finance/
  __init__.py
  procedures.py
  evidence.py
  model_audit.py
  capital_analysis.py
  opportunity.py
  compliance.py
  human_review.py
  finance_bench.py
```

## Browser Special Authority

```text
sentinel-control/services/sentinel-core/sentinel/organs/browser/
  reliability_profile.py
  session_policy.py
  fingerprint_risk.py
  compliance_gate.py
  detection_bench.py
```

## Brain Runtime Wiring

```text
sentinel-control/services/sentinel-core/sentinel/agent/brain_runtime.py
sentinel-control/services/sentinel-core/sentinel/agent/brain_pipeline.py
sentinel-control/services/sentinel-core/sentinel/agent/brain_trace.py
sentinel-control/services/sentinel-core/sentinel/agent/brain_final_gate_adapter.py
```

## Security

```text
sentinel-control/services/sentinel-core/sentinel/security/
  authority_validator.py
  context_trust_scanner.py
  secret_redactor.py
  prompt_injection_scanner.py
```

## Tests

```text
tests/test_organ_contracts.py
tests/test_organ_promotion_gate.py
tests/test_agent_lab_harvest_references.py
tests/test_financial_services_harvest_contract.py
tests/test_cloak_browser_power_review_contract.py
tests/test_p6_external_organ_foundry.py
tests/test_p6_premortem_scenarios.py
```

