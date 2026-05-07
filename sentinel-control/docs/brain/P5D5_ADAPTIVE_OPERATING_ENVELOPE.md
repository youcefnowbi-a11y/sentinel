# P5D.5 Adaptive Operating Envelope

Date: 2026-05-07
Status: Doctrine tranche

## Purpose

P5D.5 defines a future separation between root authority and adaptive operating
parameters.

The key rule is:

```text
The user grants hard boundaries.
Signals update the operating strategy.
Sentinel reallocates inside the boundaries.
Crossing a boundary requires an AuthorityExtensionProposal.
```

## RootAuthorityEnvelope

`RootAuthorityEnvelope` is the fixed mandate. It may include:

```text
budget_max
allowed_categories
allowed_tools
allowed_actions
allowed_accounts
allowed_vendors
allowed_assets
forbidden_actions
max_loss
expiry
receipt_required
ledger_required
approval_required_for_categories
```

Root authority cannot be modified by:

```text
signals
agent outputs
memory
workspace facts
market movement
expected profit
expected information gain
```

If a profitable action requires crossing root authority, Sentinel must propose
an `AuthorityExtensionProposal` and wait for explicit approval.

## AdaptiveOperatingEnvelope

`AdaptiveOperatingEnvelope` is derived from root authority plus current signals.
It may adjust:

```text
max_single_transaction
category_sub_budgets
agent_count
max_parallel_agents
exploration_budget
exploitation_budget
stop_loss
kill_switch_threshold
opportunity_ranking
vendor_preference
latency_budget
confidence_threshold
```

These parameters are allowed to move continuously as evidence changes, as long
as they remain inside the root authority.

## SignalLedger

`SignalLedger` records the observations that justify operating changes:

```text
market response
API prices
tool availability
prospect reply rate
ad metrics
conversion rate
trading volatility when trading is authorized
ROI evidence
risk changes
budget remaining
belief confidence
contradiction findings
compliance warnings
```

Signals must be traceable. A changed operating envelope without signal evidence
is not valid.

## BudgetReallocator

`BudgetReallocator` moves capital toward stronger opportunities and away from
weak ones.

It may:

```text
increase a transaction limit for a high-signal authorized route
decrease a transaction limit when risk rises
move budget from ads to API/data if API evidence is stronger
cut trading exposure if volatility or contradiction rises
hold budget in reserve when evidence is weak
scale an opportunity only after measurable signal
```

It may not:

```text
increase total budget_max
create a new allowed category
add a new account/vendor/asset outside root authority
ignore max loss
ignore expiry
skip receipts
activate forbidden actions
```

## Dynamic Limit Shape

Future implementations should compute spend limits from signal state, not fixed
magic numbers:

```text
max_single_transaction =
min(
  budget_remaining,
  root_category_cap,
  risk_adjusted_limit,
  confidence_scaled_limit,
  stop_loss_remaining
)
```

If signal quality improves, a limit may rise. If risk rises, budget tightens, or
the action becomes less reversible, the limit should fall.

## Trace Requirement

Every adaptive-envelope update should eventually emit a trace containing:

```text
previous_operating_parameters
new_operating_parameters
signal_refs
budget_remaining
risk_delta
confidence_delta
authority_boundary_check
reason
```

P5D.5 does not implement this trace event. It locks the required future shape.
