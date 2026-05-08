# P4A CDP AX And DOMSnapshot Plan

Status: implemented as Sentinel-native normalization adapters

P4A introduces runtime-payload adapters for native browser perception outputs. The adapters do not start private sessions and do not execute arbitrary page scripts.

## CDP AX Tree

`BrowserCdpAccessibilityAdapter` normalizes:

- node id
- backend node id
- role
- name
- value
- description
- states
- child ids
- ignored flag
- runtime ref id

It emits `BROWSER_CDP_AX_TREE_CAPTURED` with:

- tree id
- tree hash
- node count
- backend node count
- root id
- public/stateless boundary flags

## DOMSnapshot

`BrowserDomSnapshotAdapter` normalizes:

- tag
- role/name/text
- attributes
- DOM path
- parent index
- visibility
- interactability
- layout bounding box
- runtime ref id

It emits `BROWSER_DOM_SNAPSHOT_CAPTURED` with:

- snapshot id
- snapshot hash
- node count
- layout count
- public/stateless boundary flags

## UIObservation Bridge

Both adapters can feed `BrowserUIObservationBuilder`, which creates a single reasoning surface for Browser-Cortex and Browser-LLM.

## V2.5 Limit

These adapters are perception contracts only. Browser V3 authority classes remain outside P4A.
