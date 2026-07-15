<!-- markdownlint-disable-file -->
# Release Changes: Field Picks and Distinctive League Colors

**Related Plan**: field-picks-distinctive-colors-plan.instructions.md
**Implementation Date**: 2026-07-15

## Summary

Implement The Field draft option with one-field-per-league enforcement and post-draft field resolution across analytics, exports, persistence, and distinctive deterministic league coloring, then complete final startup and core-flow validation.

## Changes

### Added

* None.

### Modified

* draft.py
	* Extended canonical pick normalization to include stable defaults for `pick_type`, `is_field`, `field_scope`, and `field_value` while preserving legacy string and dict pick compatibility.
	* Added `get_drafted_field_leagues` helper to identify leagues that already have a drafted field pick.
	* Added right-column `The Field` controls in the draft room with one-field-per-league enforcement in both UI disable logic and commit-time guard.
	* Refactored pick commit flow into a shared `commit_pick` helper so normal team picks and field picks advance turn/round/page consistently.
	* Added league-level field resolution helpers (`compute_field_values_by_league`, `resolve_field_picks_in_drafts`) with [0, 100] clamping and invalid-field fallback notes for missing league metadata.
	* Integrated resolved field values into finished-page standings, top selections, ownership analytics, round-grid odds labels, and warning messaging.
	* Expanded flat CSV output with field-semantic columns: League, Pick Type, Pick-Time Probability, Field Value, and Resolved Probability.
	* Updated persisted snapshot payload composition to include field metadata and resolved probability details for reproducible history.
	* Replaced low-saturation hashed league palette generation with a curated high-contrast categorical palette and deterministic hash-based assignment.
	* Added deterministic collision fallback probing to avoid duplicate color assignment while palette capacity remains.
	* Upgraded `_text_color_for_background` to contrast-ratio selection between dark and light foreground colors for improved readability on saturated backgrounds.

* .copilot-tracking/plans/2026-07-15/field-picks-distinctive-colors-plan.instructions.md
	* Marked all Phase 2 implementation and validation checklist items complete.
	* Marked all Phase 3 implementation and validation checklist items complete.
	* Marked all Phase 4 validation and reporting checklist items complete.

* .copilot-tracking/plans/logs/2026-07-15/field-picks-distinctive-colors-log.md
	* Recorded Phase 2 discrepancy status and validation evidence summary.
	* Recorded Phase 3 implementation path alignment and validation evidence summary.
	* Recorded Phase 4 full validation evidence across startup, snake/non-snake core flows, and field-resolution/export regression checks.

### Removed

* None.

## Additional or Deviating Changes

* None.

## Release Summary

Phases 1 through 4 complete: field drafting, post-draft field semantics, deterministic high-contrast league coloring, and final validation/reporting are implemented and documented.
