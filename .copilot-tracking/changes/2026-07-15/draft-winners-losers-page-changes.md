<!-- markdownlint-disable-file -->
# Release Changes: Draft Winners and Losers Page

**Related Plan**: draft-winners-losers-page-plan.instructions.md
**Implementation Date**: 2026-07-15

## Summary

Implement winners and losers standings, historical persistence, and setup/data guardrails for the Streamlit draft flow.

## Changes

### Added

* draft.py - Added refresh helper to fetch latest league probabilities at draft completion.
* draft.py - Added standings aggregation helper that computes rank, picks count, total odds, and average odds per drafter.
* draft.py - Added finished-page winners and losers standings section with sorted ranking table and winner/loser callouts.
* draft.py - Added persistent draft snapshot writer that stores rank, odds, picks, and timestamp in draft_history.jsonl.

### Modified

* .copilot-tracking/plans/2026-07-15/draft-winners-losers-page-plan.instructions.md - Updated scope and marked Phase 1 implementation steps as complete.
* .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md - Updated implementation strategy to re-fetch probabilities at draft completion and added historical persistence phase.
* .copilot-tracking/plans/logs/2026-07-15/draft-winners-losers-page-log.md - Recorded user decisions and accepted implementation-path changes.
* draft.py - Updated results CSV helper to keep existing export schema while supporting string and dict pick inputs.
* draft.py - Stored selected leagues in session state for finished-page probability refresh scope.
* .copilot-tracking/plans/2026-07-15/draft-winners-losers-page-plan.instructions.md - Marked Phase 2 implementation steps complete.
* draft.py - Hardened Kalshi fetch handling with timeout, safe parsing, and zero-sum normalization guard.
* draft.py - Added setup-time guardrails for unique drafter names, required league selection, and non-empty draft pool.
* .gitignore - Ignored .agents/ and draft_history.jsonl runtime-generated artifacts.
* .copilot-tracking/plans/2026-07-15/draft-winners-losers-page-plan.instructions.md - Marked Phases 1 through 5 complete after validation.
* .copilot-tracking/plans/logs/2026-07-15/draft-winners-losers-page-log.md - Recorded validation completion and follow-on deprecation cleanup item.

### Removed

* None.

## Additional or Deviating Changes

* Switched standings scoring to end-of-draft probability refresh based on user decision.
* Promoted historical persistence from follow-on item into current scope based on user decision.
* Environment blocker was resolved by configuring the project virtual environment and installing required Python packages.
  * make app startup now succeeds.
* End-to-end validation was completed with a one-round draft run in the browser and verified persistence output creation.
* Streamlit startup regenerated .agents/ helper folder; it was removed per user request and ignored in .gitignore.

## Release Summary

Completed all planned phases for winners/losers standings, historical persistence, and guardrails.

Files affected:
* Added: None
* Modified: draft.py, .gitignore, .copilot-tracking/plans/2026-07-15/draft-winners-losers-page-plan.instructions.md, .copilot-tracking/details/2026-07-15/draft-winners-losers-page-details.md, .copilot-tracking/plans/logs/2026-07-15/draft-winners-losers-page-log.md, .copilot-tracking/changes/2026-07-15/draft-winners-losers-page-changes.md
* Removed: runtime-generated .agents/ and draft_history.jsonl validation artifact

Validation:
* make app startup smoke check passed.
* End-to-end draft completion validated standings rendering and persistence file write behavior.
