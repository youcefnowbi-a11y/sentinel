# P6A External Organ Foundry Spec

## Goal

Create the foundation for external organs without enabling real external
execution by default.

## Models To Define In P6A

```text
ExternalOrganContract
ExternalOrganRegistry
OrganAuthorityEnvelope
OrganRiskProfile
OrganDryRunReceipt
OrganExecutionReceipt
OrganReplayRecord
OrganKillSwitch
OrganPromotionGate
VendorHarvestReference
```

## Required Rule

No organ can execute until it has:

```text
contract
authority mapping
risk profile
dry-run format
receipt format
trace events
fake benchmark
promotion gate
kill switch
FinalGate compatibility
```

## Not In P6A

```text
no payment runtime
no trading runtime
no account creation runtime
no credential access
no new browser powers
no channel send
no sidecar execution
no shell execution
```

