# P4H-R Failure Analysis

Date: 2026-04-30
Status: Complete

## Verdict Class

```text
browser_fluency_first_subset_partial
```

## Partial Missions

The first scorecard has:

```text
15 partial missions
30 not-run missions
```

## Important Gaps

### 1. Lifecycle / Navigation

Partial:

```text
crash recovery
redirect F4 proof
SPA route epoch proof
```

Reason:

```text
contracts exist, but the fluency runner does not yet exercise stable 30-run
fixtures for crash and dynamic-route recovery.
```

### 2. Forms

Partial:

```text
autocomplete
credential/payment boundary as full F4 fluency
```

Reason:

```text
form authority exists, but modern form UX needs dropdown/autocomplete fixtures
and stronger credential/payment detection tasks.
```

### 3. Network / HAR / JS

Partial:

```text
allowlisted JS F4 proof
network failure repair
```

Reason:

```text
JS and HAR contracts exist, but fluency requires adversarial network fixtures
and repair-quality scoring.
```

### 4. Safety

Partial:

```text
CAPTCHA / bot-wall stop
```

Reason:

```text
Sentinel should stop or escalate, but P4H-R has not yet built a dedicated
fixture page for CAPTCHA/bot-wall recognition.
```

### 5. Cognitive Integration

Partial:

```text
repair loop
loop detector
EvidenceChain update
SuccessEvaluator browser proof
modality escalation
```

Reason:

```text
the components exist, but the fluency runner needs end-to-end fixtures proving
browser events move the brain, not just browser contracts.
```

## Non-Run Groups

These groups remain F0 in the first scorecard because they were outside the
requested critical subset:

```text
visual/OCR
cookies/storage/session
files/download/upload/PDF
multi-tab
research browsing
```
