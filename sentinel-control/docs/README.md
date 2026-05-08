# Sentinel Control Docs

Date: 2026-04-28
Status: Canonical documentation index

This folder is organized by decision domain. Keep root clean: every document
should live in the folder that owns its subject.

## Start Here

1. `brain/README.md` - current certified brain boundary.
2. `architecture/SENTINEL_AGENT_MASTER_ARCHITECTURE.md` - mission OS architecture.
3. `architecture/SENTINEL_AGENT_IMPLEMENTATION_ROADMAP.md` - implementation order.
4. `audits/SENTINEL_CORE_V1_CERTIFICATION.md` - current certification record.
5. `mission-os/SECURITY_MODEL.md` - product security model.
6. `release/RELEASE_CLEAN_ROOM_POLICY.md` - final product scrub rule.

## Folder Map

| Folder | Owns |
| --- | --- |
| `brain/` | Agent brain lock, runtime, authority, replay, evidence, final gate, review matrix. |
| `architecture/` | System architecture, roadmaps, foundry direction. |
| `mission-os/` | Mission OS product rules, GTM operator, firewall/security/evidence contracts. |
| `product/` | Product-facing specs and UI mock docs. |
| `operations/` | Deployment and Codex task guidance. |
| `audits/` | Progress reports, implementation audits, certification records. |
| `release/` | Final product clean-room and release hygiene rules. |

## Documentation Rule

Do not leave new long-form docs in this root. Add them to the correct domain
folder and update that folder's `README.md`.

Vendor research material belongs in `../agent-lab/`, not in this product docs
tree. The final product distribution must not contain third-party agent names,
raw vendor source maps, vendor audit trails, or lab-only comparison docs.
