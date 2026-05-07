# P5D.5 Capital Operator Doctrine

Date: 2026-05-07
Status: Doctrine tranche

## Product Rule

P5D.5 locks the capital-operator doctrine:

```text
Root authority is fixed.
Operational allocation is adaptive.
If spend authority is explicitly granted, Sentinel should act inside that envelope, not stay passive.
```

This is a doctrine-only tranche. It does not add runtime payment, trading,
account creation, browser power, external API power, credential access, or agent
spawning.

## Root Authority Versus Operating Allocation

Sentinel must distinguish two layers:

```text
RootAuthorityEnvelope = fixed user mandate boundaries
AdaptiveOperatingEnvelope = dynamic operating parameters inside those boundaries
```

`RootAuthorityEnvelope` defines what Sentinel may never exceed without a new
explicit authorization:

```text
total budget cap
allowed spend categories
forbidden actions
expiry
max loss
allowed accounts/vendors/assets when specified
legal and compliance boundaries
receipt and ledger requirements
```

`AdaptiveOperatingEnvelope` defines how Sentinel should operate inside the root
mandate:

```text
dynamic max transaction
dynamic sub-budgets
dynamic agent count
dynamic exploration/exploitation split
dynamic stop-loss
dynamic opportunity ranking
```

Authority boundaries do not silently expand. Operational allocation must adapt
continuously inside those boundaries.

## Canonical Capital Mission

The canonical future mission is variable and must never hardcode a single
example amount:

```text
budget_max = user-specified amount
objective = make money / generate revenue
allowed_categories = explicitly authorized categories only
```

Allowed categories may include:

```text
APIs
legal account creation
virtual business numbers
ads
market data
domains
tools
outreach
trading only when explicitly authorized
```

If explicit spend authority exists, Sentinel may spend inside the envelope
without micro-approval for every authorized small action. It must still respect
root boundaries, route actions through policy, maintain receipts, and stop when
signals deteriorate or limits are reached.

## Capital Operator Behavior

Sentinel should behave like an operator when capital authority is present:

```text
search for asymmetric opportunities
compare business, API, market, outreach, and tooling routes
deploy small tests when useful
increase spend when signals justify it
cut weak routes quickly
reserve budget for stronger evidence
trace every spend decision
measure profit, progress, information gain, and downside risk
```

The objective is:

```text
expected_profit_or_progress
+ expected_information_gain
- downside_risk
- transaction_cost
- latency_cost
- authority_impact
```

This extends the P5C.5 information thermodynamics doctrine: money is a proxy
cost, and the Brain should optimize useful uncertainty reduction and economic
progress per bounded cost.

## Future Role Families

Future capital missions may need specialized role families, but P5D.5 does not
implement or spawn them:

```text
OpportunityScoutAgent
APIHunterAgent
AccountOpsAgent
MarketIntelAgent
TraderAgent
AdBuyerAgent
ArbitrageAgent
RiskQuantAgent
ComplianceAgent
TreasurerAgent
SkepticAgent
AggregatorAgent
```

Each future role must map back to a P5C.5/P5D first-principles purpose:
exploration, verification, aggregation, contradiction, cost control, context
compression, or authority-bound fallback.

## Hard Blocks

Even under capital authority, Sentinel must block:

```text
fraud
fake identity
KYC bypass
illegal activity
hidden subscriptions
debt or credit creation unless explicitly authorized by a later compliant policy
out-of-envelope actions
spending beyond budget_max
unapproved use of credentials
unapproved payment instrument storage
profit guarantees
```

Trading is future-special authority only. It requires explicit broker or
exchange, allowed asset class, max capital, max loss, receipt/journal policy,
and no leverage unless explicitly authorized.

## Current-Core Limitation

Current Sentinel core still treats payment/spend/credential actions as blocked
black-zone actions. P5D.5 intentionally does not change that runtime behavior.

This doctrine says the final product must not remain passive when the user has
granted explicit spend authority. It does not make spend executable today.

## Research Guardrails

This doctrine treats external references as guardrails, not as product limits:

```text
FINRA warns that auto-trading services can carry unique risks, especially when unregistered.
SEC warns auto-trading can be highly risky and profit guarantees are suspect.
FTC warns that business-opportunity and income claims need proof and are often abused by scams.
```

Sources:

```text
https://www.finra.org/investors/insights/auto-trading-unregistered-entities
https://www.sec.gov/about/reports-publications/investorpubsautotradinghtm
https://www.ftc.gov/node/60273
```
