<!-- markdownlint-disable-file -->
# Research: Multi-Sport Draft Pool, Round Grid Results, and Detailed Winners Analytics

## Scope

Plan a Streamlit enhancement for three requested outcomes:

* Expand Draft Pool to include eight additional sports and Kalshi IDs.
* Redesign finished draft results into a round-by-round grid with league color coding and optional odds display.
* Expand winners and losers analytics with top selections per drafter and league ownership analysis.

## Sources

* User request in current conversation on 2026-07-15.
* .copilot-tracking/research/subagents/2026-07-15/multi-sport-draft-board-analytics-subagent-research.md.
* draft.py current implementation state.

## User-Provided Requirements

* Add these leagues and IDs to setup and draft data pull:
  * WNBA: kxwnba-26
  * MLB: kxmlb-26
  * F1 Belgian Grand Prix: kxf1race-belgp26
  * NFL: kxsb-27
  * College Basketball: kxmarmad-27
  * UCL: kxucl-27
  * NBA: kxnba-27
  * NHL: kxnhl-27
* Final draft results should be a grid where rows are rounds and columns are drafter names.
* Each pick cell should be color coded by league.
* Add toggle or separate view to append odds alongside team names.
* Create more detailed winners and losers analysis:
  * top selections per drafter
  * by-league summed odds per drafter
  * assign each league to the drafter with highest summed odds.
* Follow best design practices and reduce redundancy.
* Split into additional files only when justified.

## Verified Codebase Findings

* Current app remains a single-file Streamlit state machine in draft.py.
* LEAGUES mapping exists in draft.py and can be extended directly.
* Draft picks are currently appended as team strings during selection, which is insufficient for robust round-grid and by-league analytics.
* Finished page currently renders:
  * flat results table
  * winners and losers standings
  * persistence snapshot logic.
* Existing helpers duplicate some pick parsing logic that can be centralized.

## Architecture Direction

Selected path for this scope:

* Keep implementation in draft.py for now.
* Introduce canonical structured pick objects at draft time to remove ambiguity and reduce repeated parsing.
* Add dedicated helper layer for:
  * pick normalization
  * round-grid generation
  * league color palette generation
  * detailed analytics derivation.

Rationale:

* The app is still small and single-entry.
* Changes are cohesive around one flow.
* A helper-first refactor delivers maintainability without introducing multi-file import complexity.

## Risks and Mitigations

* Duplicate team names across leagues:
  * Mitigation: include league in each pick payload and use league plus team composite keys.
* League ownership ties:
  * Mitigation: explicit co-owner output when values tie within tolerance.
* Styling constraints in Streamlit dataframes:
  * Mitigation: use pandas Styler first; keep text fallback if style rendering is inconsistent.
* Historical compatibility with existing string picks in snapshots:
  * Mitigation: normalization helper supports both legacy string and new dict shapes.

## File-Structure Decision

* No new Python module files are required for this change set.
* Keep single-file implementation with clearer helper separation.
* Revisit extraction into analytics.py only if helper count and complexity continue growing after this scope.

## Validation Surface

* make app for startup validation.
* Manual flow validation for snake and non-snake drafts.
* Manual verification:
  * expanded leagues appear and fetch data
  * round-grid layout and color coding
  * odds toggle output
  * winners analytics and league ownership output
  * persistence remains stable.

## Open Decisions and Default Planning Assumptions

* League ownership grouping:
  * Default: treat each league label as separate ownership category, including UCL and Premier League.
* Winners metric:
  * Default: use pick-time odds for detailed analytics and preserve existing refreshed-odds standings as separate view.
* Ownership tie handling:
  * Default: display co-owners list.
* Round-grid empty cells:
  * Default: display em dash marker.
* CSV outputs:
  * Default: keep flat CSV and add a second round-grid CSV.
