# P4A UIObservation Model

Status: implemented

`BrowserUIObservation` is the unified V2.5 perception record. It lets the brain and LLM reason over a page through runtime-minted observations instead of raw page content.

## Sources

Supported sources:

- `accessibility_snapshot`
- `cdp_ax_tree`
- `dom_snapshot`
- `screenshot_region`
- `zoom_region`
- `network_delta`

## Contract

Each observation can bind:

- URL
- tab id
- frame id
- runtime ref id
- role/name/text
- bounding box
- visibility/interactability
- DOM path or AX path
- screenshot hash
- page hash
- snapshot hash
- uncertainty score
- trace refs

Observation sets include:

- `observation_set_id`
- `observation_sha256`
- `source_count`
- `observation_count`
- public/stateless boundary flags

## FinalGate

FinalGate rejects:

- missing observation set payload;
- hash mismatch;
- observation count mismatch;
- missing or invalid source count;
- non-stateless boundary flags.

The model is evidence. It is not authority, and it does not grant new browser actions.
