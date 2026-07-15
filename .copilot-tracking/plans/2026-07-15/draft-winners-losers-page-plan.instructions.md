---
applyTo: '.copilot-tracking/changes/2026-07-15/draft-winners-losers-page-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Draft Winners and Losers Page

## Overview

Add a post-draft winners/losers section that ranks drafters by summed win probabilities of their drafted selections, sorted highest to lowest, and persist historical draft/standings snapshots.

## Objectives

### User Requirements

* Show which drafter has the best chance of winning after the draft by summing odds of each drafted selection and sorting descending. Source: User conversation request (2026-07-15)
* Expand scope to include persistent historical drafts and standings. Source: User decision on 2026-07-15.
* Use end-of-draft probability re-fetch for standings if it reduces computation cost, accepting small drift from draft-time odds. Source: User decision on 2026-07-15.

### Derived Objectives

* Compute standings by re-fetching latest probabilities at draft completion and mapping them to drafted teams. Derived from: Accepted IP-02 decision.
* Keep existing finished-page results table and CSV export behavior compatible while adding standings output. Derived from: Current user-visible workflow in finished page.
* Add guardrails for duplicate drafter names and unstable API data to reduce runtime failures during setup. Derived from: Identified medium-risk constraints in research.
* Persist completed draft results and standings for historical analysis in local repository storage. Derived from: In-scope WI-02 user decision.

## Context Summary

### Project Files

* draft.py - Single-file Streamlit app containing setup, draft, and finished state flows.
* Makefile - Contains app launch command for smoke validation.
* README.md - Minimal project description, no additional validation workflow.

### References

* .copilot-tracking/research/2026-07-15/draft-winners-losers-page-research.md - Primary planning research and constraints.
* .copilot-tracking/research/subagents/2026-07-15/draft-winners-losers-subagent-research.md - Detailed architecture findings with line references.

### Standards References

* /Users/kdatta/.vscode/extensions/ise-hve-essentials.hve-core-3.2.2/.github/instructions/hve-core/markdown.instructions.md - Markdown authoring rules applied to planning artifacts.
* /Users/kdatta/.vscode/extensions/ise-hve-essentials.hve-core-3.2.2/.github/instructions/hve-core/writing-style.instructions.md - Style guidance for concise, professional planning language.

## Implementation Checklist

### [x] Implementation Phase 1: End-Of-Draft Standings Aggregation Foundation

<!-- parallelizable: false -->

* [x] Step 1.1: Add probability refresh helper for selected leagues at draft completion
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 12-30)
* [x] Step 1.2: Add winners/losers aggregation helper using refreshed odds and deterministic ranking
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 32-51)
* [x] Step 1.3: Validate phase changes
  * Run app startup smoke validation with make app

### [x] Implementation Phase 2: Finished Page Winners/Losers UI

<!-- parallelizable: true -->

* [x] Step 2.1: Render standings table sorted from highest to lowest total odds
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 63-81)
* [x] Step 2.2: Preserve compatibility of final results CSV output with string-based draft picks
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 83-98)
* [x] Step 2.3: Validate phase changes
  * Run app startup and finished-page smoke validation with make app

### [x] Implementation Phase 3: Historical Persistence

<!-- parallelizable: false -->

* [x] Step 3.1: Add persistent storage helper for completed draft snapshots
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 109-126)
* [x] Step 3.2: Persist completed draft picks and standings at finish time
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 128-145)
* [x] Step 3.3: Validate persistence behavior
  * Run app startup and complete one draft flow to verify history file writes

### [x] Implementation Phase 4: Setup and Data-Quality Guardrails

<!-- parallelizable: false -->

* [x] Step 3.1: Add setup validation for unique names and non-empty pool
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 156-173)
* [x] Step 3.2: Harden API fetch and probability normalization error handling
  * Details: .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md (Lines 175-190)
* [x] Step 3.3: Validate phase changes
  * Run setup-path smoke testing via make app

### [x] Implementation Phase 5: Validation

<!-- parallelizable: false -->

* [x] Step 4.1: Run full project validation
  * Execute available validation command: make app
* [x] Step 4.2: Fix minor validation issues
  * Iterate on straightforward runtime and UI regressions
* [x] Step 4.3: Report blocking issues
  * Document issues requiring additional research or re-planning

## Planning Log

See .copilot-tracking/plans/logs/2026-07-15/draft-winners-losers-page-log.md for discrepancy tracking, implementation paths considered, and suggested follow-on work.

## Dependencies

* Streamlit and pandas runtime available in local environment
* Kalshi API reachability for setup-time market data

## Success Criteria

* Finished page includes drafter standings sorted by summed win probability descending. Traces to: User requirement for winners/losers ranking.
* Standings computation re-fetches probabilities at draft completion and maps drafted teams to refreshed odds. Traces to: User-approved IP-02 implementation path.
* Existing final draft results table and downloadable CSV continue to function. Traces to: Current finished-page behavior baseline.
* Setup flow prevents duplicate drafter names and handles fetch/normalization failures without app crash. Traces to: Research constraints and risks section in primary research document.
* Completed drafts and standings are persisted for historical analysis. Traces to: User-approved scope expansion for WI-02.
