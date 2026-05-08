# 03 Tool Intelligence Layer

Date: 2026-04-26

## 1. Thesis

The future Sentinel must not only have tools.

It must know:

- which tools exist;
- which tools are relevant to a mission;
- which tools are safe;
- which tools are fresh;
- which tools are reliable;
- which tools require auth;
- which tools cost money;
- which tools can be replaced;
- which tools can be composed into a workflow;
- which tools must never be called under current authority.

Tools are not the power. Tool intelligence is the power.

## 2. Source Catalogs

Seed catalogs:

- `public-apis/public-apis`
  - community-curated public APIs across many categories;
  - useful as raw catalog source, not as trusted execution source.

- `public-api-lists/public-api-lists`
  - curated list of hundreds of APIs across dozens of categories;
  - provides website/search and JSON API.

Future source types:

- MCP registries;
- Postman public collections;
- RapidAPI-style marketplaces;
- government open-data portals;
- academic/science APIs;
- finance/open banking APIs;
- ecommerce and app-store datasets;
- GitHub awesome lists;
- SaaS API docs;
- browser extensions and public schemas;
- local CLI tools;
- local desktop sidecars.

## 3. Core Components

### 3.1 ToolRegistry

Stores known tools and capability manifests.

Fields:

```json
{
  "id": "tool_marketstack",
  "name": "Marketstack",
  "domain": "finance",
  "capabilities": ["stock_market_data", "historical_prices"],
  "auth_type": "api_key",
  "official_url": "https://...",
  "docs_url": "https://...",
  "cost_model": "free_tier|paid|unknown",
  "rate_limit": "unknown",
  "freshness": "real_time|delayed|static|unknown",
  "data_sensitivity": "public",
  "side_effects": ["network_read"],
  "risk_level": "low|medium|high|critical",
  "mission_use_cases": ["market_research", "trend_validation"],
  "test_status": "untested|passed|failed|degraded",
  "last_tested_at": null,
  "replacements": []
}
```

### 3.2 CapabilityManifest

Every tool needs a manifest before it can be used.

Required sections:

- identity;
- owner/source;
- auth requirements;
- inputs;
- outputs;
- side effects;
- rate limits;
- cost;
- domains contacted;
- data stored;
- sensitive data touched;
- allowed mission types;
- forbidden mission types;
- dry-run behavior;
- trace schema;
- rollback/containment;
- tests.

### 3.3 APICartographer

Imports catalogs and converts raw API listings into normalized tool candidates.

It does not call the APIs during import.

It extracts:

- category;
- auth type;
- HTTPS/CORS indicators;
- description;
- endpoint/docs URL;
- potential mission use cases;
- expected risk class;
- missing metadata.

### 3.4 ToolBench

Tests a tool before trust.

Checks:

- docs reachable;
- endpoint reachable if no-auth/sandbox is allowed;
- response schema stable;
- freshness;
- latency;
- rate limit behavior;
- error behavior;
- data usefulness;
- cost/auth requirement;
- privacy implications;
- replacement availability.

ToolBench never uses leaked keys.

Allowed credentials:

- no-auth public endpoint;
- official free tier;
- user-provided key;
- OAuth granted by user;
- sandbox key;
- internal test key.

Forbidden:

- leaked API keys;
- keys copied from GitHub;
- credentials embedded in vendor examples;
- bypassed auth.

### 3.5 ToolGraph

Models tool composition.

Example:

```text
jobs API -> hiring signal
reviews API -> pain evidence
pricing pages -> WTP signal
news API -> timing signal
competitor scraper -> alternative map
=> opportunity confidence
```

ToolGraph edges:

- input compatibility;
- output dependency;
- evidence type generated;
- confidence contribution;
- cost contribution;
- risk contribution;
- replacement path.

### 3.6 MissionToToolCompiler

Compiles mission objective into required tool capabilities.

Input:

```text
"Find a product opportunity in ecommerce returns"
```

Output:

```json
{
  "needed_capabilities": [
    "market_news",
    "ecommerce_reviews",
    "shopify_app_discovery",
    "competitor_pricing",
    "reddit_or_community_signals",
    "jobs_trend",
    "public_web_research"
  ],
  "required_methods": [
    "cross_domain_signal_arbitrage",
    "contradiction_mining",
    "evidence_ladder"
  ],
  "blocked_without_approval": [
    "login",
    "form_submit",
    "external_contact",
    "paid_api_call"
  ]
}
```

## 4. Tool Scoring

Initial deterministic score:

```text
tool_score =
  20 * mission_relevance
+ 15 * data_freshness
+ 15 * reliability
+ 10 * documentation_quality
+ 10 * replacement_availability
+ 10 * low_cost
+ 10 * low_auth_friction
+ 10 * safety_fit
- 20 * sensitive_data_risk
- 20 * external_mutation_risk
- 15 * unknown_terms_risk
```

Scores are not truth. They are routing aids.

Every score must show which facts generated it.

## 5. Tool Risk Classes

| Class | Meaning | Example | Default Route |
| --- | --- | --- | --- |
| static_reference | no execution, docs/catalog only | API list entry | auto import |
| read_only_public | public GET/no-auth or sandbox | weather endpoint | auto or log |
| read_only_auth | user key/OAuth required | finance data | escalate for credential scope |
| private_data_read | user/private account read | CRM contacts | escalate |
| draft_only_write | creates local draft | email draft | auto if scoped |
| external_mutation | sends, posts, buys, submits | email send | escalate or block |
| host_mutation | changes local machine/code | shell, desktop, prod write | block until later gated |

## 6. First Implementation Target

G14A should implement:

- `ToolRegistry`
- `CapabilityManifest`
- catalog import from static fixture;
- public API candidate normalizer;
- no live API calls yet except optional no-auth test fixtures;
- fake ToolBench;
- mission-to-tool compiler v0;
- tests proving unsafe tools do not become executors.

## 7. Why This Makes Sentinel Stronger

OpenClaw and JARVIS show what happens when raw power enters runtime early.

Sentinel should do the opposite:

```text
discover tools
-> classify tools
-> benchmark tools
-> compose tools
-> bind tools to mission authority
-> execute only through policy
```

That is how Sentinel becomes more than an agent with a bag of tools.
