# P4A Public Multi-Tab Plan

Status: implemented

`BrowserPublicMultitabOperator` executes public multi-tab strategies through the existing public lifecycle controller.

## Contract

Each tab plan includes:

- URL
- purpose
- optional tab id

The operator:

- starts a public/stateless session;
- opens each tab through URL policy checks;
- enforces `max_tabs`;
- emits a strategy event with tab ids and final URLs.

## Event

`BROWSER_MULTITAB_STRATEGY_EXECUTED` includes:

- session id
- tab ids
- tab count
- max tabs
- final URLs
- lifecycle trace refs
- public/stateless boundary flags

## FinalGate

FinalGate rejects:

- tab count over max;
- tab id count mismatch;
- final URL count mismatch;
- missing lifecycle trace refs;
- stateful boundary flags.

## V2.5 Limit

Multi-tab is public evidence orchestration only. Private session and credentialed flows remain non-delegated.
