# Sentinel Super Agent Blueprint

Date: 2026-04-26
Status: G10 architecture spec, amended by G11 Power Mode doctrine and G12 Mission Authority doctrine, no runtime implementation authorized

## Mission

Sentinel is an original proof-backed agent architecture.

It rewrites useful mechanisms from OpenClaw, Hermes, OpenJarvis, and JARVIS without integrating vendor code:

```text
see -> verify -> research -> debate -> decide -> plan -> simulate -> approve -> execute_safe -> trace -> learn
```

Sentinel has two product faces:

- Sentinel GTM Operator: converts evidence into a sellable GTM pack.
- Sentinel Control: governs risky agent actions through policy, simulation, approval, budget, and trace.

G11 product correction:

- Sentinel should be aggressive in safe, reversible, local, and draft-only zones.
- Sentinel should be controlled when actions become irreversible, external, sensitive, or costly.
- Future Power Mode is scoped authority, not a global bypass.

G12 product correction:

- Mission Authority is the primary agentic primitive.
- Power Mode is one authority level inside a mission.
- Sentinel should receive a mission, operate inside its mandate, and escalate only at the boundary.

## Non-Negotiable Boundary

Allowed now:

- CueIdea evidence import.
- Research enrichment.
- GTM pack generation.
- File generation under generated-project boundaries.
- Draft-only outreach.
- Static scanner work.
- Fake benchmarks.
- Architecture specs.

Blocked now:

- real email send;
- real browser submit;
- shell execution;
- desktop automation;
- sidecar runtime;
- vendor bridge;
- unscanned skills;
- auto-code modification;
- payment/spend action;
- production mutation.

## Super Agent Genome

| Gene | Purpose | Vendor lesson | Sentinel implementation principle |
|---|---|---|---|
| Evidence Authority | Business decisions need proof | Vendors can act without business evidence | Every recommendation cites evidence or gap |
| Capability Manifest | No hidden tools | Skills/plugins/sidecars hide power | Every tool/skill/sidecar/channel declares permissions |
| Firewall Kernel | Actions need control | OpenClaw/JARVIS runtime surfaces | propose -> score -> dry-run -> approve -> execute -> trace |
| Memory Without Authority | Context without hidden policy | Hermes/JARVIS memory injection | Memory cannot approve, permit, or override |
| Cost-Aware Reasoning | Spend is a safety issue | OpenJarvis routing | Budget gates every run |
| Skill Quarantine | Skills are supply chain | OpenClaw/Hermes/OpenJarvis | scan, hash, classify, fake-eval, approve |
| Read-Only Browser First | Web research before web action | OpenClaw/JARVIS browser control | no submit/send/publish in v1 |
| Permissioned Sidecar Later | Host control is critical | JARVIS sidecar | deny-by-default, scoped, revocable, later only |
| Learning As Proposal | Improve without mutation | Hermes/OpenJarvis learning | proposals only, user applies |
| Trace As Product Memory | Trust requires reconstruction | all vendors | trace every trust-changing event |

## Architecture

```text
Input Gateway
  -> Context Classifier
  -> Mission Gateway
  -> Mission Authority Envelope
  -> Evidence Ledger
  -> Research Enrichment
  -> Debate Engine
  -> Decision Planner
  -> Action Kernel
  -> Firewall
       -> PolicyEngine
       -> RiskScorer
       -> BudgetGate
       -> DryRunSimulator
       -> ApprovalGate
  -> Safe Executors v1
  -> Trace Ledger
  -> Learning Proposals
```

## Product Modes

| Mode | Meaning | UI Label | Allowed outputs |
|---|---|---|---|
| Evidence-backed | CueIdea or cited research evidence exists | Evidence-backed | GTM pack, verdict, safe files, drafts |
| Sandbox hypothesis | No source-backed evidence yet | Sandbox / hypothesis mode | hypothesis pack, evidence gaps, research questions |
| Firewall review | Actions proposed but not executed | Needs approval | dry-runs and approval decisions |
| Blocked | Policy rejects action | Blocked | explanation, safer alternative |

## Authority Modes

| Mode | Meaning | Current status |
|---|---|---|
| Safe Mode | Fast local and draft-only execution after policy check | allowed for v1 safe executors |
| Operator Mode | Preview and approval for bounded impact actions | design/limited approval path |
| Power Mode | Future scoped authority envelopes for high-impact capabilities | spec only, disabled |
| Autonomous Mode | Future pre-approved playbooks with caps and review | not authorized |

## Mission Authority

Mission Authority defines the real delegation contract:

- objective;
- success criteria;
- expected artifacts;
- allowed systems;
- allowed tools;
- allowed actions;
- forbidden actions;
- duration;
- max actions;
- max cost;
- risk appetite;
- escalation triggers;
- stop and revoke controls.

The action lattice is evaluated inside the mission:

- green: in-scope and reversible;
- amber: in-scope and recoverable;
- red: in-scope but external, irreversible, sensitive, costly, or low confidence;
- black: forbidden, out-of-scope, or unavailable runtime.

## Primary Interfaces

### EvidenceItem

- source;
- url/source ref;
- quote/summary;
- type;
- direct/adjacent/weak proof class;
- confidence;
- freshness;
- relevance;
- sensitivity.

### DecisionPlan

- verdict;
- confidence;
- risk score;
- evidence refs;
- evidence gaps;
- proposed actions.

### AgentAction

- tool;
- intent;
- input;
- expected output;
- risk level;
- approval requirement;
- policy version;
- evidence refs.

### TraceRecord

- event type;
- input snapshot;
- decision snapshot;
- action snapshot;
- output snapshot;
- cost;
- policy version;
- timestamp.

## Future Power Tracks

Future tracks stay disabled until fake benchmarks and policy specs pass:

- BrowserSandbox.
- ChannelAdapters.
- PermissionedSidecar.
- WorkflowEngine.
- DesktopAwareness.
- PowerMode authority envelopes.

## North Star

Sentinel becomes the control layer that turns raw autonomous power into proof-backed, budget-aware, permissioned business operation.
