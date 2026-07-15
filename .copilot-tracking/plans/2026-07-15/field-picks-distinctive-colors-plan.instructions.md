---
applyTo: '.copilot-tracking/changes/2026-07-15/field-picks-distinctive-colors-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Field Picks and Distinctive League Colors

## Overview

Add a draftable The Field option across selected leagues, resolve field values post-draft as undrafted share, integrate field semantics into finished-page analytics and exports, and upgrade league colors to a more distinctive deterministic palette.

## Objectives

### User Requirements

* Add The Field as a draft option for all selected leagues. Source: User conversation request on 2026-07-15.
* Field picks represent ownership of undrafted teams in that league. Source: User conversation request on 2026-07-15.
* Field can be drafted without live odds during draft room flow. Source: User conversation request on 2026-07-15.
* Post-draft field value equals 100 minus drafted share for that league. Source: User conversation request on 2026-07-15.
* Place field controls in easiest low-risk location (right side or top of pool). Source: User conversation request on 2026-07-15.
* Enforce one-field-per-league so only one field selection is allowed per league in a draft. Source: User conversation request on 2026-07-15.
* Make league colors more distinctive. Source: User conversation request on 2026-07-15.
* Plan this task before implementation. Source: User conversation request on 2026-07-15.

### Derived Objectives

* Preserve single-file architecture in draft.py for this scope to reduce integration overhead. Derived from: Current architecture and selected implementation path.
* Keep backward compatibility for legacy pick payloads while extending canonical pick metadata. Derived from: Existing normalization helper usage and persistence compatibility requirements.
* Apply field semantics consistently across standings, analytics, exports, and snapshot persistence. Derived from: Research findings on downstream data consumers.

## Context Summary

### Project Files

* draft.py - Streamlit setup, draft, finished UI and all analytics/persistence helpers.
* Makefile - Startup validation command.
* requirements.txt - Runtime dependency declarations for deployment.

### References

* .copilot-tracking/research/2026-07-15/field-picks-distinctive-colors-research.md - Primary research for feature scope, algorithms, and risks.
* .copilot-tracking/research/subagents/2026-07-15/field-pick-and-color-distinctiveness-research.md - Code-path mapping and implementation alternatives.

### Standards References

* /Users/kdatta/.vscode/extensions/ise-hve-essentials.hve-core-3.2.2/.github/instructions/hve-core/markdown.instructions.md - Markdown conventions for planning artifacts.
* /Users/kdatta/.vscode/extensions/ise-hve-essentials.hve-core-3.2.2/.github/instructions/hve-core/writing-style.instructions.md - Markdown writing style conventions.

## Implementation Checklist

### [x] Implementation Phase 1: Canonical Field Pick Model and Draft Controls

<!-- parallelizable: false -->

* [x] Step 1.1: Extend canonical pick normalization with field metadata
  * Details: .copilot-tracking/details/2026-07-15/field-picks-distinctive-colors-details.md (Lines 12-29)
* [x] Step 1.2: Add right-column The Field draft controls in draft room
  * Details: .copilot-tracking/details/2026-07-15/field-picks-distinctive-colors-details.md (Lines 33-53)
  * Enforce one-field-per-league lock (disable or block duplicate field picks for the same league)
* [x] Step 1.3: Validate phase changes
  * Run make app and draft-room smoke test including field pick action

### [x] Implementation Phase 2: Post-Draft Field Resolution and Analytics Integration

<!-- parallelizable: false -->

* [x] Step 2.1: Add league-level field resolver helper(s)
  * Details: .copilot-tracking/details/2026-07-15/field-picks-distinctive-colors-details.md (Lines 67-87)
  * Include explicit invalid-field fallback for missing league metadata (resolve 0.0 with user-visible note)
* [x] Step 2.2: Integrate resolved field values in standings and analytics
  * Details: .copilot-tracking/details/2026-07-15/field-picks-distinctive-colors-details.md (Lines 88-110)
* [x] Step 2.3: Update exports and persistence with field semantics
  * Details: .copilot-tracking/details/2026-07-15/field-picks-distinctive-colors-details.md (Lines 111-133)
* [x] Step 2.4: Validate phase changes
  * Run make app and verify finished-page field calculations and downloads
  * Execute full field scenario matrix from research (baseline, single field, duplicate field blocked, all drafted, none drafted)
  * Validation executed with make app startup plus scripted resolver smoke scenarios for baseline, single-field, duplicate-field lock semantics, all-drafted equals 0, and none-drafted equals 100

### [x] Implementation Phase 3: Distinctive League Color Palette Upgrade

<!-- parallelizable: false -->

* [x] Step 3.1: Replace palette logic with deterministic high-contrast mapping
  * Details: .copilot-tracking/details/2026-07-15/field-picks-distinctive-colors-details.md (Lines 153-173)
* [x] Step 3.2: Validate readability and contrast in styled grid
  * Details: .copilot-tracking/details/2026-07-15/field-picks-distinctive-colors-details.md (Lines 174-190)
* [x] Step 3.3: Validate phase changes
  * Run make app and verify legend and table distinction across leagues

### [x] Implementation Phase 4: Final Validation and Reporting

<!-- parallelizable: false -->

* [x] Step 4.1: Run full project validation
  * Executed `PATH="$PWD/.venv/bin:$PATH" make app` and verified Streamlit startup on localhost.
  * Executed deterministic core-flow checks for snake and non-snake turn progression with expected pick orders.
  * Executed quick field-resolution and CSV regression checks for resolved field values and export semantics.
* [x] Step 4.2: Fix minor validation issues
  * No application runtime or rendering issues were identified in this phase.
  * One scripted assertion failed due to a test expectation mismatch on dataframe string formatting, not due to application behavior.
* [x] Step 4.3: Report blocking issues and follow-on recommendations
  * Recorded validation evidence and follow-on notes in planning and changes logs.
  * No blocking issues identified for scope completion.

## Planning Log

See .copilot-tracking/plans/logs/2026-07-15/field-picks-distinctive-colors-log.md for discrepancy tracking, implementation paths considered, and suggested follow-on work.

## Dependencies

* Python virtual environment with streamlit, pandas, and requests.
* Kalshi API availability for selected leagues and finished-page data refresh pathways.
* Browser validation access for draft-room and finished-page checks.

## Success Criteria

* Users can draft The Field for any selected league with explicit canonical metadata.
* Only one field pick per league is allowed and duplicate attempts are prevented.
* Finished-page field values are computed as undrafted share and reflected in standings and analytics.
* CSV exports and persisted snapshots include field semantics while preserving compatibility.
* Round-grid league colors are visibly more distinctive and remain readable.
* Existing non-field draft flows remain functional without regressions.