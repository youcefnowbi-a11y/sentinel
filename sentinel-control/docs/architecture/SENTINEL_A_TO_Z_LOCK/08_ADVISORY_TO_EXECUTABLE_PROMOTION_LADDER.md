# Advisory To Executable Promotion Ladder

## Levels

```text
L0 vendor observation
L1 extraction matrix
L2 Sentinel contract
L3 fake eval
L4 dry-run
L5 sandbox
L6 limited execution
L7 production-scoped execution
L8 continuous OrganBench monitoring
```

## Promotion Requirements

Every organ phase must declare:

```text
current promotion level
target promotion level
blocked promotion levels
required evidence to promote
rollback/demotion criteria
```

## Non-Negotiable Rule

No organ reaches L6 until it has:

```text
contract
authority mapping
risk profile
dry-run receipt
execution receipt
trace events
fake benchmark
kill switch
FinalGate compatibility
```

