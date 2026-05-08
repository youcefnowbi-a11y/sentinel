# P4A Verifier And Loop Detector Spec

Status: implemented

P4A adds a verifier and loop detector so browser actions are followed by explicit post-state checks.

## Post-Action Verifier

`BrowserPostActionVerifier` checks:

- receipt mission id;
- after snapshot receipt presence;
- after snapshot hash binding;
- expected URL, when supplied;
- expected text, when supplied.

It emits `BROWSER_VERIFICATION_COMPLETED` with:

- verification id
- verdict
- checked receipt id
- before/after snapshot hashes
- expected condition count
- findings
- trace ref count

Verdicts:

- `accepted`
- `needs_repair`
- `inconclusive`

## Loop Detector

`BrowserLoopDetector` detects repeated state keys such as:

```text
action_kind:ref_id:page_hash
```

It emits `BROWSER_LOOP_DETECTED` when the repeat threshold is reached.

## FinalGate

FinalGate rejects:

- verifier events without receipt id;
- verifier events without snapshot hashes;
- accepted verifier events with findings;
- loop events where repeated count is below threshold;
- loop events without loop key;
- non-stateless boundary flags.
