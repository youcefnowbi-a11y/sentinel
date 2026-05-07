# P5D.5 Signal Responsive Spend Policy

Date: 2026-05-07
Status: Doctrine tranche

## Purpose

`DynamicSpendPolicy` is the future policy that decides when Sentinel should
spend, hold, scale, cut, or ask for a new authority boundary during capital
missions.

P5D.5 is doctrine-only. It does not add executable spend.

## SpendDecisionTrace

Every future spend decision must produce a traceable record:

```text
mission_id
root_authority_ref
adaptive_operating_envelope_ref
opportunity_id
requested_amount
vendor_or_target
category
reason
expected_profit_or_progress
expected_information_gain
downside_risk
transaction_cost
latency_cost
authority_fit
budget_remaining_before
budget_remaining_after
receipt_required
stop_condition
rollback_or_cancel_path
signal_refs
decision
```

The trace must prove that the decision stayed inside root authority.

## Decision Outcomes

The policy may return:

```text
spend_authorized_by_existing_envelope
hold_for_more_evidence
reduce_amount
reallocate_to_stronger_route
stop_route
kill_mission
propose_authority_extension
block_forbidden_action
```

`spend_authorized_by_existing_envelope` means the future runtime may proceed
only if every existing authority, policy, receipt, and risk gate passes.

## Signal-Responsive Behavior

The policy should adapt to signals:

```text
strong prospect replies -> raise outreach/tooling allocation inside root cap
poor ad metrics -> cut ads and preserve budget
API price increase -> recalculate cost per information gain
compliance warning -> stop route or lower exposure
trading volatility spike -> reduce or stop trading exposure
budget drawdown -> tighten transaction size
high-confidence ROI evidence -> scale authorized route
contradictory evidence -> route to skeptic/verifier before spend
```

The policy must not treat an initial max transaction as permanent. The maximum
transaction is an operating parameter, not a root boundary, unless the user
explicitly made it a root boundary.

## Micro-Approval Rule

If the user grants explicit spend authority with a clear root envelope, Sentinel
should not ask for micro-approval for every small authorized transaction.

It must ask or propose extension when:

```text
the transaction crosses budget_max
the category is not allowed
the vendor/account/asset is outside root authority
the transaction exceeds a root max-single-transaction if one exists
the action requires credentials not granted
the action creates debt, credit, or hidden recurring obligation
the action enters trading authority not explicitly granted
policy requires preview or approval
```

## Trading Authority

Trading is not generally unlocked by a vague "make money" mission.

Future trading execution requires explicit root authority:

```text
allowed broker or exchange
allowed asset class
max trading capital
max loss
position size rules
leverage policy
stop-loss policy
journal and receipt policy
expiry
```

Without those fields, trading remains blocked or proposal-only.

## Anti-Scam And Compliance Policy

Capital missions must reject:

```text
guaranteed profit claims
business opportunities without evidence
unregistered auto-trading delegation without risk review
fake accounts or identity misrepresentation
KYC bypass
spam or illegal outreach
hidden subscriptions
irreversible spend without authority fit
```

This policy is what lets Sentinel be aggressive without becoming reckless.

## Current-Core Limitation

Current core still blocks payment/spend/credential actions through the static
black-zone model. P5D.5 records the future doctrine but does not change runtime
behavior.
