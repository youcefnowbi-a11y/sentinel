# Release Clean-Room Policy

Date: 2026-04-28
Status: Final-product requirement

## Purpose

The finished Sentinel product must be Sentinel-native. It must not contain
third-party agent branding, raw source dumps, transplant notes, or visible
research fingerprints in product code, product docs, packaged assets, generated
templates, UI labels, public APIs, or release folders.

Research can guide architecture during development. It must not ship.

## Separation Rule

Allowed during research:

```text
agent-lab/
```

Not allowed in final product distribution:

```text
sentinel-control/docs/* vendor research dumps
sentinel-control/services/** vendor names or copied runtime code
sentinel-control/apps/** vendor names or copied UI/runtime code
raw vendor trees
forensic reports naming source agents
extraction matrices naming source agents
integration notes naming source agents
```

## Final Scrub Scan

Before a release artifact is cut, run a case-insensitive scan over the product
tree for all research-source names and aliases used during development.

Example:

```powershell
rg -n -i -f <internal_research_scrub_terms.txt> sentinel-control
```

Release acceptance requires:

- zero matches in product source code;
- zero matches in shipped product docs;
- zero matches in UI copy, API names, generated templates, and package metadata;
- zero raw vendor source files or trees;
- zero vendor audit reports in the release artifact.

Internal historical docs may remain in the development repository only if the
release packaging excludes them and the release scrub scan is run on the final
artifact, not just the working tree.

## Clean-Room Rewrite Rule

Any feature inspired by research must be rewritten as a Sentinel-native concept:

- product names must be Sentinel names;
- modules must expose Sentinel contracts;
- tests must assert Sentinel behavior;
- docs must describe Sentinel architecture only;
- comments must not mention the source specimen.

The final code should read as if Sentinel was designed from first principles,
because the research artifacts were only temporary scaffolding.

## Release Gate

No release is accepted unless a release reviewer records:

```text
scan_command:
scan_scope:
matches_found:
release_artifact_path:
reviewer:
decision: pass | fail
```

Any match fails release unless it is inside an explicitly non-shipping archive
that is absent from the release artifact.
