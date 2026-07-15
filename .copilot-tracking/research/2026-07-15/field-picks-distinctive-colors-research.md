<!-- markdownlint-disable-file -->
# Research: Field Picks and Distinctive League Colors

## Scope

Plan a Streamlit enhancement that adds a new draftable option called The Field across user-selected leagues and improves league color distinctiveness in finished-round grid rendering.

## Sources

* User request in current conversation on 2026-07-15.
* .copilot-tracking/research/subagents/2026-07-15/field-pick-and-color-distinctiveness-research.md.
* draft.py current implementation state.

## User-Provided Requirements

* Add The Field as a draft option for any user-selected league.
* The Field means ownership of all undrafted teams in that league.
* The Field does not require live odds during draft; draft-time display can be oddless.
* After draft completion, each field pick value is 100 minus the sum of drafted non-field selections in that league.
* Place field controls either on the right side or top of available draft pool, favoring easier integration.
* Make league colors more distinctive.
* Allow only one The Field pick per league across the full draft.
* Plan the task before implementation.

## Verified Codebase Findings

* App architecture is single-file and state-driven in draft.py with setup, draft, and finished phases.
* Current canonical pick shape is normalized via normalize_pick_entry with compatibility handling for legacy string picks.
* Draft commit path uses pool row button actions and appends structured picks.
* Finished page computes standings, top selections, ownership analytics, and exports from normalized picks.
* Current league palette uses hashed hue with low saturation and can produce similar pastel shades.

## Architecture Direction

Selected path for this scope:

* Keep implementation in draft.py.
* Extend canonical pick model with explicit field metadata while preserving legacy behavior.
* Add a compact field-draft control in the right column to avoid destabilizing pool row rendering logic.
* Resolve field values post-draft using league-level subtraction from 100.
* Use deterministic high-contrast categorical league palette with hash-based assignment.

Rationale:

* Lowest regression risk for existing row-based pool interactions.
* Minimal structural churn aligned with user guidance to split files only if needed.
* Deterministic color assignment improves readability and consistency between reruns.

## Field Resolution Model

Recommended formula per league:

* field_value = clamp(100 - sum(prob_at_pick for drafted non-field picks in league), 0, 100)

Application strategy:

* Only one field pick per league is valid across the full draft.
* If all teams are drafted, field_value resolves to 0.
* If no non-field teams are drafted in a league with field, field_value resolves to 100.
* If field pick has missing league, treat as invalid for field computation and assign 0 with a user-visible note.

## Analytics and Export Impact

* Round-grid labeling must support field picks, with odds toggle showing resolved field value after draft.
* Flat CSV should include league, pick type, and resolved field value.
* Winners and losers standings must incorporate resolved field values for field picks.
* Top selections and ownership matrix should include field picks using resolved field value.
* Snapshot persistence should include field metadata and resolved values to preserve reproducibility.

## Risks and Mitigations

* Mixed odds semantics risk: non-field refreshed odds vs field pick-time-derived values.
  * Mitigation: select one consistent standings policy and document decision.
* Field lock checks could be bypassed by malformed session payloads.
  * Mitigation: enforce one-field-per-league in both UI controls and normalization-time validation helpers.
* Palette collisions can still occur with many leagues.
  * Mitigation: use curated categorical palette with deterministic fallback stepping.

## Open Decisions and Planning Defaults

* Field multiplicity rule (same league): fixed to one field pick per league across the draft.
* Standings probability basis: default to pick-time consistency for field and non-field picks to avoid mixed semantics.
* Top-selections inclusion: default to include field picks as rankable selections.
* Field availability rule: enforce one-field-per-league lock in draft-room controls.

## Validation Surface

* make app startup and state smoke tests.
* Manual draft runs for snake and non-snake flows.
* Scenario tests:
  * no field picks
  * one field pick in one league
  * second field pick in same league is blocked
  * all teams drafted in league with field
  * no teams drafted in league with field
* Verify exports, standings, top selections, ownership, and persisted snapshots include expected field semantics.