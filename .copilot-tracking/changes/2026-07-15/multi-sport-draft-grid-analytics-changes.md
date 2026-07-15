<!-- markdownlint-disable-file -->
# Release Changes: Multi-Sport Draft Grid and Analytics

**Related Plan**: multi-sport-draft-grid-analytics-plan.instructions.md
**Implementation Date**: 2026-07-15

## Summary

Implemented expanded multi-sport draft coverage, round-grid results redesign, and detailed winners analytics with centralized normalization and validated compatibility.

## Changes

### Added

* draft.py - Added normalize_pick_entry helper to centralize parsing and metadata defaults for legacy and canonical pick records.
* draft.py - Added normalize_drafter_picks and normalize_all_drafts helpers to reuse canonical pick normalization across helper pipelines.
* draft.py - Added round-grid result helpers for rounds-by-drafters table shaping, odds label formatting, and league-based cell styling.
* draft.py - Added stable league palette generation and legend rendering for finished-page color-coded draft results.
* draft.py - Added top-selections analytics helper using pick-time probabilities with deterministic per-drafter ranking.
* draft.py - Added league ownership analytics helper for by-league summed odds matrix and majority or co-owner summary.

### Modified

* draft.py - Expanded LEAGUES with WNBA, MLB, F1 Belgian Grand Prix, NFL, College Basketball, UCL, NBA, and NHL Kalshi IDs.
* draft.py - Switched draft commit storage to structured pick payloads including team, league, prob_at_pick, round, pick_in_round, and overall_pick.
* draft.py - Updated results CSV, standings, and persistence helpers to consume normalized picks with backward compatibility for historical string picks.
* .copilot-tracking/plans/2026-07-15/multi-sport-draft-grid-analytics-plan.instructions.md - Marked Phase 1 complete.
* draft.py - Replaced primary finished-page results display with round-grid table and added odds toggle control.
* draft.py - Preserved flat CSV and added round-grid CSV export download.
* .copilot-tracking/plans/2026-07-15/multi-sport-draft-grid-analytics-plan.instructions.md - Marked Phase 2 complete.
* draft.py - Added finished-page Top Selections, League Ownership Matrix, and League Ownership Summary sections with readable explanatory captions.
* draft.py - Extended draft snapshot persistence schema with optional analytics payload while preserving existing standings fields.
* .copilot-tracking/plans/2026-07-15/multi-sport-draft-grid-analytics-plan.instructions.md - Marked Phase 3 complete.
* draft.py - Refactored results, standings, ownership analytics, top-picks analytics, and persistence helpers to consume shared normalized pick collections.
* .copilot-tracking/plans/2026-07-15/multi-sport-draft-grid-analytics-plan.instructions.md - Marked Phase 4 complete.

### Removed

* None.

## Additional or Deviating Changes

* Validation required PATH override to use the local virtual environment streamlit executable.
	* make app succeeded with PATH="$PWD/.venv/bin:$PATH".
* Streamlit emitted existing deprecation warnings for use_container_width during phase validation.
	* Warning is non-blocking and tracked as follow-on cleanup.
* Completed quick finished-page flow validation with a one-round two-drafter draft at http://localhost:8502.
	* Verified Top Selections, League Ownership Matrix, and League Ownership Summary all render in finished state.
	* Verified persisted snapshot now includes analytics block with top selections and league ownership summary.
* Completed Phase 4 smoke startup validation with PATH="$PWD/.venv/bin:$PATH" make app.
  * Verified Streamlit boot reaches setup page startup without regressions after helper refactor.
* Final Phase 5 validation completed successfully with PATH="$PWD/.venv/bin:$PATH" make app.
	* No syntax or diagnostics errors in draft.py.

## Release Summary

Completed Phases 1 through 5.

Files affected:
* Added: None
* Modified: draft.py, .copilot-tracking/plans/2026-07-15/multi-sport-draft-grid-analytics-plan.instructions.md, .copilot-tracking/plans/logs/2026-07-15/multi-sport-draft-grid-analytics-log.md, .copilot-tracking/changes/2026-07-15/multi-sport-draft-grid-analytics-changes.md
* Removed during validation cleanup: runtime-generated .agents/ and draft_history.jsonl artifacts

Validation:
* Startup validation passed via PATH="$PWD/.venv/bin:$PATH" make app.
* Finished-page flow checks passed for round grid, odds toggle, top selections, ownership matrix, ownership summary, and analytics-aware persistence schema.
