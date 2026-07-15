<!-- markdownlint-disable-file -->
# Research: Draft Winners and Losers Page

## Scope

Plan a Streamlit enhancement to add post-draft winner/loser insights by summing drafted team win probabilities per drafter and ranking drafters from highest to lowest total odds.

## Sources

* User request from conversation on 2026-07-15
* .copilot-tracking/research/subagents/2026-07-15/draft-winners-losers-subagent-research.md

## Verified Findings

* The application is a single-file Streamlit state machine with setup, draft, and finished branches in draft.py (Lines 100-236), draft.py (Lines 237-490), and draft.py (Lines 491-544).
* Drafted picks are currently stored as team-name strings only, created at draft init in draft.py (Lines 219-222) and appended during draft actions in draft.py (Lines 408-412).
* Probabilities are fetched and normalized in get_event within draft.py (Lines 58-86), then shown in the pool UI in draft.py (Lines 383-399).
* Drafted rows are removed from the mutable pool in draft.py (Lines 415-419), which means no explicit probability payload is retained with each pick after selection.
* Final results currently show only Drafter, Pick, Team via create_results_csv in draft.py (Lines 31-42) and finished page rendering in draft.py (Lines 496-522).

## Constraints and Risks

* A winners/losers ranking cannot be computed robustly from current pick storage because picks do not include probability data.
* Duplicate drafter names can collide in the drafts dictionary (keyed by name), introducing aggregation ambiguity.
* Remote API calls in get_event lack defensive error handling for network and schema failures.
* Probability normalization assumes a non-zero denominator and can fail if all markets have zero bid/ask-derived values.

## Recommended Planning Direction

* Preserve existing draft flow while introducing a canonical pick record shape that stores team, league, and probability at draft time.
* Add a dedicated aggregation helper that sums per-drafter probabilities and returns sorted winner/loser standings.
* Extend the finished page with an additional standings section that displays sorted totals from highest to lowest while keeping existing CSV output intact for compatibility.
* Add setup-time validation for unique drafter names and an actionable error state when no valid pool data is available.

## Validation Surface

* Makefile currently provides app run command only: make app.
* No explicit automated tests or lint commands are documented in README.md.

## Open Questions

* Loser definition: full ranking table versus explicitly labeled bottom-N block.
* Tie-breaking policy when summed probabilities are equal.
* Whether winners/losers standings should also have a dedicated downloadable CSV.
