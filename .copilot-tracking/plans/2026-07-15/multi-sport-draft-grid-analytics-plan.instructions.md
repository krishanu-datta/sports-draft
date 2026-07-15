---
applyTo: '.copilot-tracking/changes/2026-07-15/multi-sport-draft-grid-analytics-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Multi-Sport Draft Grid and Analytics

## Overview

Expand the draft pool leagues, redesign final results into a color-coded round-grid view with optional odds labels, and add detailed winners and losers analytics while reducing redundant pick-processing logic.

## Objectives

### User Requirements

* Add requested sports and Kalshi IDs to Draft Pool configuration and draft-time selection flow. Source: User conversation request on 2026-07-15.
* Display final draft results as rounds-by-drafters grid with sport-based color coding. Source: User conversation request on 2026-07-15.
* Add a toggle or separate view to append odds next to each selection label. Source: User conversation request on 2026-07-15.
* Add detailed winners and losers view including top selections and league ownership attribution by summed odds. Source: User conversation request on 2026-07-15.
* Follow best code design practices and remove redundancy. Source: User conversation request on 2026-07-15.

### Derived Objectives

* Introduce canonical structured pick payloads to support deterministic round-grid and by-league analytics. Derived from: DR-01 in planning log.
* Keep single-file architecture for now and only refactor helper organization to reduce complexity overhead. Derived from: Selected implementation path and user split-only-if-needed guidance.
* Preserve existing outputs and persistence behavior while adding new views and exports. Derived from: Current finished-page baseline and compatibility goals.

## Context Summary

### Project Files

* draft.py - Current single-file Streamlit app containing setup, draft, and finished views.
* Makefile - Run command for app startup smoke validation.
* .gitignore - Runtime artifact ignore configuration.

### References

* .copilot-tracking/research/2026-07-15/multi-sport-draft-grid-analytics-research.md - Primary research and assumptions for this scope.
* .copilot-tracking/research/subagents/2026-07-15/multi-sport-draft-board-analytics-subagent-research.md - Code-level insertion points and risk analysis.

### Standards References

* /Users/kdatta/.vscode/extensions/ise-hve-essentials.hve-core-3.2.2/.github/instructions/hve-core/markdown.instructions.md - Markdown conventions for planning artifacts.
* /Users/kdatta/.vscode/extensions/ise-hve-essentials.hve-core-3.2.2/.github/instructions/hve-core/writing-style.instructions.md - Style and wording conventions for markdown updates.

## Implementation Checklist

### [x] Implementation Phase 1: League Expansion and Canonical Pick Model

<!-- parallelizable: false -->

* [x] Step 1.1: Expand LEAGUES with requested Kalshi IDs
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 12-32)
* [x] Step 1.2: Convert draft picks to canonical structured payloads with compatibility normalization
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 34-53)
* [x] Step 1.3: Validate phase changes
  * Run setup and startup smoke checks with make app

### [x] Implementation Phase 2: Round-Grid Final Results View

<!-- parallelizable: false -->

* [x] Step 2.1: Add round-grid transformation helpers
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 66-84)
* [x] Step 2.2: Add league color coding and odds toggle to finished-page grid view
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 86-105)
* [x] Step 2.3: Add round-grid export while preserving flat CSV
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 107-119)
* [x] Step 2.4: Validate phase changes
  * Run make app and complete one draft to verify grid rendering and toggle behavior

### [x] Implementation Phase 3: Detailed Winners and Losers Analytics

<!-- parallelizable: false -->

* [x] Step 3.1: Add top selections per drafter analytics section
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 130-148)
* [x] Step 3.2: Add league ownership matrix and majority or co-owner summary
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 150-168)
* [x] Step 3.3: Integrate analytics into persistence snapshot schema
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 170-185)
* [x] Step 3.4: Validate phase changes
  * Run make app and verify detailed sections and persistence behavior

### [x] Implementation Phase 4: Redundancy Reduction and Helper Cleanup

<!-- parallelizable: false -->

* [x] Step 4.1: Centralize pick normalization logic used across helpers
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 196-212)
* [x] Step 4.2: Keep single-file architecture with clearer helper boundaries
  * Details: .copilot-tracking/details/2026-07-15/multi-sport-draft-grid-analytics-details.md (Lines 213-225)
* [x] Step 4.3: Validate phase changes
  * Run make app smoke regression for setup, draft, and finished paths

### [x] Implementation Phase 5: Final Validation and Reporting

<!-- parallelizable: false -->

* [x] Step 5.1: Run full project validation
  * Execute make app and end-to-end manual checks
* [x] Step 5.2: Fix minor validation issues
  * Address straightforward UI and runtime issues found during smoke tests
* [x] Step 5.3: Report blocking issues and follow-on recommendations
  * Record unresolved decisions and follow-on items in planning log and changes doc

## Planning Log

See .copilot-tracking/plans/logs/2026-07-15/multi-sport-draft-grid-analytics-log.md for discrepancy tracking, implementation paths considered, and pending decisions.

## Dependencies

* Python virtual environment with streamlit, pandas, requests
* Kalshi API availability for league event fetches
* Browser validation access for finished-page UI checks

## Success Criteria

* Draft Pool includes all requested additional leagues and fetches draftable entries.
* Finished-page results primary view is a round-grid table with league color coding.
* Odds toggle appends or hides per-pick odds in grid labels.
* Detailed winners and losers sections show top picks and league ownership attribution.
* Redundant pick-parsing logic is centralized and maintainable.
* Existing draft flow, exports, and persistence remain functional.
