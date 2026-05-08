# 04 Work Method Library

Date: 2026-04-26

## 1. Thesis

A powerful agent needs methods, not only tools.

Tools answer: "What can I call?"

Methods answer:

```text
How should I think?
What should I test?
What evidence changes my mind?
What failure should I look for?
What is the best next action under uncertainty?
```

The Work Method Library is Sentinel's operating discipline.

## 2. Method Object

Every method should become a structured object:

```json
{
  "id": "method_contradiction_mining",
  "name": "Contradiction Mining",
  "purpose": "Find evidence that invalidates or weakens a claim",
  "inputs": ["claim", "evidence_items", "research_context"],
  "outputs": ["contradictions", "confidence_adjustment", "research_questions"],
  "best_for": ["business_decision", "research_validation", "launch_risk"],
  "not_for": ["pure creative ideation without validation"],
  "trace_required": true,
  "reviewer_checks": ["contradictions_not_hidden", "confidence_adjusted"]
}
```

## 3. Core Methods

### 3.1 Evidence Ladder

Purpose: rank proof quality.

Ladder:

```text
noise
-> anecdote
-> repeated complaint
-> direct pain
-> workaround
-> competitor payment
-> explicit willingness to pay
-> budget owner with urgency
-> purchase/order/contract
```

Use in:

- GTM;
- research;
- pricing;
- launch readiness.

Rule:

- No WTP means no ready/build verdict.

### 3.2 Contradiction Mining

Purpose: search for disconfirming evidence.

Questions:

- Who tried this and failed?
- Why did users refuse to pay?
- What cheaper substitute exists?
- What regulation blocks it?
- What platform can kill it?
- Is it just a feature?
- Can a one-person script solve it?

Use in:

- opportunity validation;
- competitor gap analysis;
- investment decisions;
- roadmap prioritization.

### 3.3 Red Team / Blue Team

Purpose: adversarial reasoning.

Flow:

```text
Blue Team: strongest case for mission/action.
Red Team: strongest case against it.
Nexus: verdict and confidence update.
```

Use in:

- high-risk business decisions;
- external sends;
- product positioning;
- architecture choices.

### 3.4 OODA Loop

Purpose: fast adaptive mission execution.

```text
Observe -> Orient -> Decide -> Act
```

Use in:

- browser research;
- launch iteration;
- sales follow-up;
- live ops.

### 3.5 Bayesian Update

Purpose: adjust confidence from evidence.

Simplified v0:

```text
prior_confidence
+ direct_proof_bonus
+ repeated_signal_bonus
+ WTP_bonus
+ competitor_payment_bonus
- contradiction_penalty
- weak_source_penalty
- stale_evidence_penalty
= posterior_confidence
```

Use in:

- decision planner;
- evidence verifier;
- reviewer.

### 3.6 Premortem

Purpose: find likely failure before action.

Prompt:

```text
Assume this mission failed after 30 days.
List the most likely reasons and the earliest signal for each.
```

Use in:

- launch plan;
- coding mission;
- tool adoption;
- outbound campaign.

### 3.7 Causal Map

Purpose: distinguish correlation from cause.

Example:

```text
job posts increasing
-> maybe market demand
-> maybe hype hiring
-> validate with budgets/pricing/customer pain
```

Use in:

- cross-domain signal arbitrage;
- market research;
- pricing.

### 3.8 ROI Tree

Purpose: connect actions to measurable outcomes.

```text
action
-> cost
-> expected evidence gained
-> expected revenue/learning
-> risk
-> next decision
```

Use in:

- mission planner;
- budget router;
- launch roadmap.

### 3.9 Constraint Solver

Purpose: turn limits into design.

Inputs:

- budget;
- time;
- available tools;
- legal constraints;
- team capacity.

Output:

- best feasible mission path.

### 3.10 Opportunity Arbitrage

Purpose: find hidden opportunities by crossing domains.

Examples:

```text
jobs trend + app store complaints + regulation + pricing pages
```

```text
weather + logistics + ecommerce reviews
```

```text
GitHub issues + enterprise job posts + compliance regulation
```

Use in:

- product opportunity discovery;
- niche selection;
- first-customer targeting.

### 3.11 Brand Narrative Distillation

Purpose: convert proof into memorable positioning.

Inputs:

- pain evidence;
- ICP;
- competitor gaps;
- emotional trigger;
- category language.

Output:

- name directions;
- tagline;
- one-liner;
- launch story;
- visual tone.

### 3.12 Systems Decomposition

Purpose: understand code, PCs, internet, electronics, or LLM systems.

Flow:

```text
surface behavior
-> components
-> interfaces
-> state
-> control flow
-> data flow
-> failure modes
-> intervention points
```

Use in:

- code intelligence;
- device/sidecar design;
- browser automation;
- API integration;
- LLM evaluation.

## 4. Method Selection

Mission planner chooses methods before tools.

Example:

```text
Mission: launch a SaaS from a CueIdea signal
Methods:
- Evidence Ladder
- Contradiction Mining
- ROI Tree
- Brand Narrative Distillation
- Premortem
Tools:
- CueIdea evidence import
- public web research
- competitor pages
- pricing extraction
- local file generator
- image/brand generator later
```

## 5. Implementation Target

G14B or G15 should add:

- method registry;
- method selection rules;
- method trace records;
- reviewer checks for missing methods;
- tests proving contradiction mining can downgrade confidence.
