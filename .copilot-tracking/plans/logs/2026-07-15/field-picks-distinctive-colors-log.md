<!-- markdownlint-disable-file -->
# Planning Log: Field Picks and Distinctive League Colors

## Discrepancy Log

Gaps and differences identified between research findings and the implementation plan.

### Unaddressed Research Items

* None.

### Plan Deviations from Research

* None.
* Phase 1 implementation matched the selected path (single-file changes in `draft.py` with right-column controls and canonical metadata extension).
* Phase 2 implementation matched the selected path (single-file resolver plus finished-page analytics/export/persistence integration in `draft.py`).
* Phase 3 implementation matched the selected path (single-file palette and contrast updates in `draft.py` with deterministic assignment).

## Phase 2 Validation Notes

* make app startup validation passed with local virtual environment PATH override and Streamlit serving on localhost.
* Scripted resolver smoke scenarios covered baseline no-field behavior, single-field partial coverage math, duplicate-field lock helper behavior, all-drafted-to-0.0, none-drafted-to-100.0, and missing-league invalid-field fallback notes.

## Phase 3 Validation Notes

* make app startup validation passed with local virtual environment PATH override and Streamlit serving on localhost.
* Deterministic palette and contrast-readability check passed in direct helper execution with 18 sample leagues.
* Minimum measured foreground-to-background contrast ratio for sampled colors was 4.168, with `NASCAR` (`#9467bd`) selecting `#111827` text.

## Phase 4 Validation Notes

* make app startup validation passed with local virtual environment PATH override and Streamlit serving on localhost.
* Core draft flow turn-order validation passed for both snake and non-snake logic using deterministic progression checks.
* Field-resolution and CSV-semantic regression check passed for resolved field value math and export shape.
* Direct `python - <<'PY'` helper scripts emit expected Streamlit bare-mode warnings when importing `draft.py`; warnings are non-blocking for helper-level checks.

## Phase 4 Discrepancies

* None.

## Implementation Paths Considered

### Selected: Single-File Field Integration with Right-Column Controls and Post-Draft Resolver

* Approach: Extend canonical pick schema, add right-column field action UI, compute post-draft field values, integrate into analytics/exports/persistence, and replace league palette with high-contrast deterministic mapping in draft.py.
* Rationale: Meets requirements with lowest regression risk in current architecture.
* Evidence: .copilot-tracking/research/2026-07-15/field-picks-distinctive-colors-research.md (Lines 42-50)

### IP-01: Synthetic The Field Rows in Available Pool

* Approach: Inject one virtual field row per selected league at top of left pool.
* Trade-offs: Keeps all picks in one panel but increases coupling with pool filtering, sorting, and row-button indexing.
* Rejection rationale: Higher regression risk than right-column controls for current code shape.

### IP-02: Immediate Multi-File Refactor with New Modules for Field and Palette

* Approach: Extract field logic and palette logic into new modules before feature implementation.
* Trade-offs: Better separation but introduces structural churn and import risks in an app that remains manageable as one file.
* Rejection rationale: Outside current need; user requested splitting only when it makes clear sense.

## Suggested Follow-On Work

* WI-01: Add color-vision accessibility mode with alternate palette presets (medium)
  * Source: Palette enhancement scope and future UX resilience
  * Dependency: Distinctive palette baseline complete
* WI-02: Add optional configuration to include or exclude field picks in top selections ranking (low)
  * Source: PD-02 scope decision
  * Dependency: Baseline field analytics implementation complete
* WI-03: Add automated integration tests for snake and non-snake end-to-end draft-room progression (medium)
  * Source: Phase 4 validation approach used deterministic scripting instead of full UI automation
  * Dependency: Introduce a lightweight test harness around draft turn-state transitions

## User Decisions Pending

* PD-01: Probability basis for standings
  * Options: Pick-time for all picks, or mixed refreshed odds for non-field picks.
  * Current planning default: Pick-time for all picks.
* PD-02: Field inclusion in top selections
  * Options: Include field picks in ranking, or exclude field picks.
  * Current planning default: Include field picks.

## Resolved Decisions

* RD-01: One-field-per-league lock is in scope and required.
  * Decision: Only one field pick is allowed per league across the full draft.
  * Source: User decision on 2026-07-15.