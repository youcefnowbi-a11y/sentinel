# Repo Governance And Dirty Tree Policy

## Purpose

Prevent phase truth loss.

## Rules

```text
Use phase-only commits.
List required files per phase.
Run git status --short before and after.
Do not include unrelated dirty-tree files.
Do not broad-refactor inside lock phases.
Update CURRENT_STATE_LOCK.md for every lock.
Record commit hashes in final reports.
Treat dirty tree files as unaccepted until committed.
```

## Commit Ledger Format

```text
phase =
commit_hash =
files_changed =
tests_run =
tests_not_run_reason =
dirty_tree_ignored =
authority_boundary_confirmed =
next_phase =
```

## Current Dirty Tree Rule

The existing dirty tree contains unrelated work in `RedditPulse`, `agent-lab`,
web app files, and core files. This architecture lock may commit only:

```text
sentinel-control/docs/CURRENT_STATE_LOCK.md
sentinel-control/docs/architecture/SENTINEL_A_TO_Z_LOCK/**
```

