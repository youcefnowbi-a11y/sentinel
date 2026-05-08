# P4E Research Browsing Tasks

Date: 2026-04-30
Status: Complete

## Purpose

The research browsing slice tests evidence quality and browser-cortex
consumption for claims and citations.

## Task Group

```text
research_browsing_citations
```

Signals:

```text
BROWSER_EVIDENCE_COLLECTED
BROWSER_CORTEX_INTERPRETED
```

The benchmark records citation count, source quality, stable refs, and a
hypothesis confidence delta.

## Scoring

- mission success;
- source quality;
- proof completeness;
- trace quality;
- Wilson interval;
- no raw browser content treated as authority.

## Boundary

This is BrowseComp-style in structure only. It does not replace a real
hard-to-find open-web research benchmark.
