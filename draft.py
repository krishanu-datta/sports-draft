import hashlib
import json
import colorsys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Draft Room",
    layout="wide"
)


# ==========================
# HELPERS
# ==========================

def prob_color(prob):
    if prob >= 25:
        return "green"
    elif prob >= 10:
        return "yellow"
    elif prob >= 5:
        return "orange"
    else:
        return "red"


def normalize_pick_entry(selection, overall_pick=None, round_number=None, pick_in_round=None):
    if isinstance(selection, dict):
        raw_pick = selection
    else:
        raw_pick = {"team": selection}

    team = str(raw_pick.get("team", "")).strip()
    league = str(raw_pick.get("league", "")).strip()

    prob_at_pick = raw_pick.get("prob_at_pick", raw_pick.get("prob", 0.0))
    try:
        prob_at_pick = float(prob_at_pick)
    except (TypeError, ValueError):
        prob_at_pick = 0.0

    def to_int(value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    normalized = {
        "team": team,
        "league": league,
        "prob_at_pick": prob_at_pick,
        "round": to_int(raw_pick.get("round", raw_pick.get("round_number"))),
        "pick_in_round": to_int(raw_pick.get("pick_in_round", raw_pick.get("pick"))),
        "overall_pick": to_int(raw_pick.get("overall_pick", raw_pick.get("overall"))),
    }

    if normalized["overall_pick"] is None and overall_pick is not None:
        normalized["overall_pick"] = to_int(overall_pick)

    if normalized["round"] is None and round_number is not None:
        normalized["round"] = to_int(round_number)

    if normalized["pick_in_round"] is None and pick_in_round is not None:
        normalized["pick_in_round"] = to_int(pick_in_round)

    return normalized


def normalize_drafter_picks(picks, include_empty=False):
    normalized_picks = []

    for fallback_overall_pick, pick in enumerate((picks or []), start=1):
        normalized_pick = normalize_pick_entry(
            pick,
            overall_pick=fallback_overall_pick,
            round_number=fallback_overall_pick,
            pick_in_round=fallback_overall_pick,
        )

        if include_empty or normalized_pick["team"]:
            normalized_picks.append(normalized_pick)

    return normalized_picks


def normalize_all_drafts(drafts, drafter_order=None, include_empty=False):
    normalized = {}
    drafters = list(drafter_order or (drafts or {}).keys())

    for drafter_name in drafters:
        normalized[str(drafter_name).strip()] = normalize_drafter_picks(
            (drafts or {}).get(drafter_name, []),
            include_empty=include_empty,
        )

    return normalized


def create_results_csv(drafts):
    rows = []

    for player, picks in drafts.items():
        normalized_picks = normalize_drafter_picks(picks, include_empty=True)
        for normalized_pick in normalized_picks:
            team = normalized_pick["team"]
            pick = normalized_pick.get("overall_pick")

            rows.append({
                "Drafter": player,
                "Pick": pick,
                "Team": team
            })

    return pd.DataFrame(rows)


def format_pick_cell_label(normalized_pick, include_odds=False):
    team_name = str(normalized_pick.get("team", "")).strip()
    if not team_name:
        return ""

    if not include_odds:
        return team_name

    probability = normalized_pick.get("prob_at_pick", 0.0)
    try:
        probability = float(probability)
    except (TypeError, ValueError):
        probability = 0.0

    return f"{team_name} ({probability:.1f}%)"


def build_round_grid_dataframe(drafts, drafter_order=None, include_odds=False, empty_marker="—"):
    drafters = list(drafter_order or (drafts or {}).keys())
    if not drafters:
        return pd.DataFrame(), pd.DataFrame()

    normalized_by_drafter = normalize_all_drafts(
        drafts,
        drafter_order=drafters,
        include_empty=True,
    )

    max_round = 0
    for drafter in drafters:
        normalized_picks = normalized_by_drafter.get(drafter, [])
        max_round = max(max_round, len(normalized_picks))
        for normalized_pick in normalized_picks:
            if normalized_pick["round"] is not None and normalized_pick["round"] > 0:
                max_round = max(max_round, normalized_pick["round"])

    if max_round == 0:
        return pd.DataFrame(index=pd.Index([], name="Round")), pd.DataFrame()

    round_index = pd.Index(range(1, max_round + 1), name="Round")
    grid = pd.DataFrame(empty_marker, index=round_index, columns=drafters)
    grid_leagues = pd.DataFrame("", index=round_index, columns=drafters)

    for drafter in drafters:
        normalized_picks = normalized_by_drafter.get(drafter, [])
        for fallback_round, normalized_pick in enumerate(normalized_picks, start=1):
            team_name = normalized_pick["team"]
            if not team_name:
                continue

            round_number = normalized_pick["round"] if normalized_pick["round"] and normalized_pick["round"] > 0 else fallback_round
            label = format_pick_cell_label(normalized_pick, include_odds=include_odds)
            league_name = str(normalized_pick.get("league", "")).strip()

            if grid.at[round_number, drafter] == empty_marker:
                grid.at[round_number, drafter] = label
            else:
                grid.at[round_number, drafter] = f"{grid.at[round_number, drafter]} / {label}"

            if league_name:
                grid_leagues.at[round_number, drafter] = league_name

    return grid, grid_leagues


def build_league_color_palette(league_names):
    palette = {}

    for league_name in sorted({str(name).strip() for name in league_names if str(name).strip()}):
        digest = hashlib.sha256(league_name.encode("utf-8")).hexdigest()
        hue = (int(digest[:8], 16) % 360) / 360.0
        red, green, blue = colorsys.hsv_to_rgb(hue, 0.22, 0.98)
        palette[league_name] = "#{:02x}{:02x}{:02x}".format(
            int(red * 255),
            int(green * 255),
            int(blue * 255),
        )

    return palette


def _text_color_for_background(hex_color):
    hex_value = hex_color.strip().lstrip("#")
    if len(hex_value) != 6:
        return "#1f2937"

    red = int(hex_value[0:2], 16)
    green = int(hex_value[2:4], 16)
    blue = int(hex_value[4:6], 16)
    luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255

    return "#111827" if luminance > 0.6 else "#f9fafb"


def style_round_grid(grid_df, league_grid_df, league_palette, empty_marker="—"):
    if grid_df.empty:
        return grid_df

    styles = pd.DataFrame("", index=grid_df.index, columns=grid_df.columns)

    for round_number in grid_df.index:
        for drafter in grid_df.columns:
            value = str(grid_df.at[round_number, drafter])
            league_name = str(league_grid_df.at[round_number, drafter]).strip()

            if value == empty_marker:
                styles.at[round_number, drafter] = "color: #9ca3af;"
                continue

            background = league_palette.get(league_name)
            if background:
                text_color = _text_color_for_background(background)
                styles.at[round_number, drafter] = (
                    f"background-color: {background}; color: {text_color}; font-weight: 600;"
                )
            else:
                styles.at[round_number, drafter] = "font-weight: 600;"

    return grid_df.style.apply(lambda _: styles, axis=None)


def get_event(event_ticker):
    event_ticker = event_ticker.upper().strip()
    empty_df = pd.DataFrame(columns=["team", "prob"])

    url = f"https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker={event_ticker}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return empty_df

    markets = payload.get("markets", []) if isinstance(payload, dict) else []
    if not isinstance(markets, list):
        return empty_df

    teams = []
    probs = []

    for market in markets:
        if not isinstance(market, dict):
            continue

        team = str(market.get("yes_sub_title", "")).strip()
        if not team:
            continue

        try:
            ask_price = float(market.get("previous_yes_ask_dollars", 0))
            bid_price = float(market.get("previous_yes_bid_dollars", 0))
        except (TypeError, ValueError):
            ask_price = 0.0
            bid_price = 0.0

        prob = 100 * (ask_price + bid_price) / 2 if (ask_price > 0 and bid_price > 0) else 0.0
        teams.append(team)
        probs.append(prob)

    if not teams:
        return empty_df

    df = pd.DataFrame({"team": teams, "prob": probs})
    df["prob"] = pd.to_numeric(df["prob"], errors="coerce").fillna(0.0)

    probability_sum = float(df["prob"].sum())
    if probability_sum > 0:
        df["prob"] = 100 * df["prob"] / probability_sum
    else:
        df["prob"] = 0.0

    return df


def refresh_selected_league_probabilities(selected_leagues):
    refreshed_frames = []

    for league_name in selected_leagues or []:
        league_ticker = LEAGUES.get(league_name)
        if not league_ticker:
            continue

        league_df = get_event(league_ticker)
        if league_df.empty:
            continue

        if "team" not in league_df.columns or "prob" not in league_df.columns:
            continue

        league_df = league_df[["team", "prob"]].copy()
        league_df["team"] = league_df["team"].astype(str).str.strip()
        league_df["prob"] = pd.to_numeric(league_df["prob"], errors="coerce").fillna(0.0)
        league_df["league"] = league_name
        refreshed_frames.append(league_df[["league", "team", "prob"]])

    if not refreshed_frames:
        return pd.DataFrame(columns=["league", "team", "prob", "lookup_key"])

    refreshed = pd.concat(refreshed_frames, ignore_index=True)
    refreshed["lookup_key"] = refreshed["league"].astype(str) + "::" + refreshed["team"].astype(str)

    return refreshed


def build_winners_losers_standings(drafts, refreshed_probabilities):
    standings_columns = [
        "rank",
        "drafter",
        "picks_count",
        "total_win_probability",
        "average_pick_probability",
    ]

    if not drafts:
        return pd.DataFrame(columns=standings_columns)

    team_probability_lookup = {}
    pick_probability_lookup = {}
    if refreshed_probabilities is not None and not refreshed_probabilities.empty:
        odds = refreshed_probabilities.copy()
        if "team" in odds.columns and "prob" in odds.columns:
            odds["team"] = odds["team"].astype(str).str.strip()
            odds["prob"] = pd.to_numeric(odds["prob"], errors="coerce").fillna(0.0)
            if "league" in odds.columns:
                odds["league"] = odds["league"].astype(str).str.strip()
            else:
                odds["league"] = ""

            odds["lookup_key"] = odds["league"] + "::" + odds["team"]

            odds = odds.sort_values(
                ["lookup_key", "team", "prob", "league"],
                ascending=[True, True, False, True],
                kind="mergesort",
            )

            pick_probability_lookup = (
                odds.drop_duplicates(subset=["lookup_key"], keep="first")
                .set_index("lookup_key")["prob"]
                .to_dict()
            )

            team_probability_lookup = (
                odds.drop_duplicates(subset=["team"], keep="first")
                .set_index("team")["prob"]
                .to_dict()
            )

    rows = []
    for drafter, picks in drafts.items():
        pick_probabilities = []

        for normalized_pick in normalize_drafter_picks(picks):
            team_name = normalized_pick["team"]
            league_name = normalized_pick["league"]

            if not team_name:
                continue

            lookup_key = f"{league_name}::{team_name}" if league_name else ""
            pick_probability = pick_probability_lookup.get(
                lookup_key,
                team_probability_lookup.get(team_name, 0.0),
            )

            pick_probabilities.append(
                float(pick_probability)
            )

        picks_count = len(pick_probabilities)
        total_probability = float(sum(pick_probabilities))
        average_probability = (total_probability / picks_count) if picks_count else 0.0

        rows.append(
            {
                "drafter": drafter,
                "picks_count": picks_count,
                "total_win_probability": total_probability,
                "average_pick_probability": average_probability,
            }
        )

    standings = pd.DataFrame(rows)
    if standings.empty:
        return pd.DataFrame(columns=standings_columns)

    standings = standings.sort_values(
        [
            "total_win_probability",
            "average_pick_probability",
            "picks_count",
            "drafter",
        ],
        ascending=[False, False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)

    standings.insert(0, "rank", standings.index + 1)

    return standings[standings_columns]


def build_top_selections_by_drafter(drafts, top_n=3, drafter_order=None):
    top_selection_columns = [
        "drafter",
        "top_pick_rank",
        "team",
        "league",
        "prob_at_pick",
        "overall_pick",
    ]

    if not drafts:
        return pd.DataFrame(columns=top_selection_columns), {}

    drafters = list(drafter_order or drafts.keys())
    rows = []
    top_picks_snapshot = {}

    try:
        top_n_value = int(top_n)
    except (TypeError, ValueError):
        top_n_value = 3
    top_n_value = max(1, top_n_value)

    for drafter_name in drafters:
        normalized_picks = normalize_drafter_picks(drafts.get(drafter_name, []))

        if not normalized_picks:
            top_picks_snapshot[drafter_name] = []
            continue

        picks_df = pd.DataFrame(normalized_picks)
        picks_df["prob_at_pick"] = pd.to_numeric(
            picks_df["prob_at_pick"], errors="coerce"
        ).fillna(0.0)
        picks_df["overall_pick"] = pd.to_numeric(
            picks_df["overall_pick"], errors="coerce"
        )

        picks_df["overall_pick_sort"] = picks_df["overall_pick"].fillna(10**9)
        picks_df["team"] = picks_df["team"].astype(str)
        picks_df["league"] = picks_df["league"].fillna("").astype(str)

        top_picks = picks_df.sort_values(
            ["prob_at_pick", "overall_pick_sort", "team", "league"],
            ascending=[False, True, True, True],
            kind="mergesort",
        ).head(top_n_value)

        top_picks_snapshot[drafter_name] = []
        for pick_rank, pick_row in enumerate(top_picks.itertuples(index=False), start=1):
            overall_pick_value = getattr(pick_row, "overall_pick", None)
            if pd.isna(overall_pick_value):
                overall_pick_value = None
            else:
                overall_pick_value = int(overall_pick_value)

            prob_at_pick_value = float(getattr(pick_row, "prob_at_pick", 0.0))
            team_name = str(getattr(pick_row, "team", "")).strip()
            league_name = str(getattr(pick_row, "league", "")).strip()

            rows.append(
                {
                    "drafter": drafter_name,
                    "top_pick_rank": pick_rank,
                    "team": team_name,
                    "league": league_name,
                    "prob_at_pick": prob_at_pick_value,
                    "overall_pick": overall_pick_value,
                }
            )

            top_picks_snapshot[drafter_name].append(
                {
                    "top_pick_rank": pick_rank,
                    "team": team_name,
                    "league": league_name,
                    "prob_at_pick": round(prob_at_pick_value, 6),
                    "overall_pick": overall_pick_value,
                }
            )

    return pd.DataFrame(rows, columns=top_selection_columns), top_picks_snapshot


def build_league_ownership_analytics(drafts, drafter_order=None, tie_tolerance=1e-9):
    drafters = list(drafter_order or (drafts or {}).keys())
    if not drafters:
        empty_matrix = pd.DataFrame()
        empty_summary = pd.DataFrame(columns=["league", "ownership", "owners", "top_total_prob"])
        return empty_matrix, empty_summary, []

    pick_rows = []
    for drafter_name in drafters:
        normalized_picks = normalize_drafter_picks((drafts or {}).get(drafter_name, []))
        for normalized_pick in normalized_picks:

            league_name = str(normalized_pick.get("league", "")).strip() or "Unknown"
            pick_rows.append(
                {
                    "league": league_name,
                    "drafter": drafter_name,
                    "prob_at_pick": float(normalized_pick.get("prob_at_pick", 0.0) or 0.0),
                }
            )

    if not pick_rows:
        empty_matrix = pd.DataFrame(columns=drafters)
        empty_summary = pd.DataFrame(columns=["league", "ownership", "owners", "top_total_prob"])
        return empty_matrix, empty_summary, []

    ownership_source = pd.DataFrame(pick_rows)
    ownership_source["prob_at_pick"] = pd.to_numeric(
        ownership_source["prob_at_pick"], errors="coerce"
    ).fillna(0.0)

    ownership_matrix = (
        ownership_source.groupby(["league", "drafter"], as_index=False)["prob_at_pick"]
        .sum()
        .pivot(index="league", columns="drafter", values="prob_at_pick")
        .fillna(0.0)
    )
    ownership_matrix = ownership_matrix.reindex(columns=drafters, fill_value=0.0)
    ownership_matrix = ownership_matrix.sort_index(kind="mergesort")

    summary_rows = []
    ownership_snapshot = []

    for league_name, totals in ownership_matrix.iterrows():
        max_total = float(totals.max())
        owners = sorted(
            [
                str(drafter_name)
                for drafter_name, total in totals.items()
                if abs(float(total) - max_total) <= tie_tolerance
            ]
        )

        if len(owners) > 1:
            ownership_mode = "Co-owner"
            owners_text = ", ".join(owners)
        else:
            ownership_mode = "Majority owner"
            owners_text = owners[0] if owners else ""

        summary_rows.append(
            {
                "league": league_name,
                "ownership": ownership_mode,
                "owners": owners_text,
                "top_total_prob": max_total,
            }
        )

        ownership_snapshot.append(
            {
                "league": str(league_name),
                "ownership": ownership_mode,
                "owners": owners,
                "top_total_prob": round(max_total, 6),
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    return ownership_matrix, summary_df, ownership_snapshot


def persist_completed_draft_snapshot(drafts, standings, analytics=None):
    if standings is None or standings.empty:
        return False

    standings_rows = []
    for row in standings.itertuples(index=False):
        drafter_name = str(getattr(row, "drafter", "")).strip()
        drafter_picks = [
            pick["team"]
            for pick in normalize_drafter_picks(drafts.get(drafter_name, []))
            if pick["team"]
        ]

        standings_rows.append(
            {
                "drafter": drafter_name,
                "rank": int(getattr(row, "rank", 0)),
                "total_odds": float(getattr(row, "total_win_probability", 0.0)),
                "average_odds": float(getattr(row, "average_pick_probability", 0.0)),
                "picks_count": int(getattr(row, "picks_count", 0)),
                "picks_list": drafter_picks,
            }
        )

    normalized_drafts = normalize_all_drafts(drafts)

    snapshot_signature_payload = {
        "drafts": normalized_drafts,
        "standings": standings_rows,
    }
    if analytics:
        snapshot_signature_payload["analytics"] = analytics

    snapshot_id = hashlib.sha256(
        json.dumps(snapshot_signature_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()

    history_path = Path(__file__).with_name("draft_history.jsonl")

    if history_path.exists():
        with history_path.open("r", encoding="utf-8") as history_file:
            for line in history_file:
                stripped = line.strip()
                if not stripped:
                    continue

                try:
                    existing_snapshot = json.loads(stripped)
                except json.JSONDecodeError:
                    continue

                if existing_snapshot.get("snapshot_id") == snapshot_id:
                    return False

    snapshot_payload = {
        "snapshot_id": snapshot_id,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "standings": standings_rows,
    }
    if analytics:
        snapshot_payload["analytics"] = analytics

    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(snapshot_payload, sort_keys=True) + "\n")

    return True


LEAGUES = {
    "US Open Men": "kxatp-26uso",
    "US Open Women": "kxwta-26uso",
    "College Football": "kxncaaf-27",
    "Premier League": "kxpremierleague-27",
    "WNBA": "kxwnba-26",
    "MLB": "kxmlb-26",
    "F1 Belgian Grand Prix": "kxf1race-belgp26",
    "NFL": "kxsb-27",
    "College Basketball": "kxmarmad-27",
    "UCL": "kxucl-27",
    "NBA": "kxnba-27",
    "NHL": "kxnhl-27",
}


# ==========================
# STATE
# ==========================

if "page" not in st.session_state:
    st.session_state.page = "setup"

if "player_inputs" not in st.session_state:
    st.session_state.player_inputs = [
        "Player 1",
        "Player 2"
    ]


# ==========================
# SETUP
# ==========================

if st.session_state.page == "setup":

    st.title("Fantasy Draft Setup")

    # ---- Drafters ----

    st.header("Drafters")

    if st.button("➕ Add drafter"):

        st.session_state.player_inputs.append(
            f"Player {len(st.session_state.player_inputs)+1}"
        )

        st.rerun()


    players = []

    for i, default in enumerate(
        st.session_state.player_inputs
    ):

        players.append(
            st.text_input(
                f"Drafter {i+1}",
                value=default,
                key=f"player_{i}"
            )
        )


    # ---- Settings ----

    st.header("Draft Settings")


    snake = st.toggle(
        "🐍 Snake Draft",
        value=True
    )


    rounds = st.number_input(
        "Number of rounds",
        min_value=1,
        max_value=100,
        value=5
    )


    # ---- Leagues ----

    st.header("Draft Pool")

    st.write(
        "Select leagues available in the draft:"
    )

    selected_leagues = st.multiselect(
        "Leagues",
        options=list(LEAGUES.keys()),
        default=list(LEAGUES.keys()),
        key="league_multiselect"
    )

    with st.spinner("Fetching Kalshi data..."):
        data = pd.DataFrame()
        for league_name in selected_leagues:
            league_ticker = LEAGUES[league_name]
            league_events = get_event(league_ticker)
            if league_events.empty:
                continue
            league_events["league"] = league_name
            data = pd.concat([data, league_events], ignore_index=True)


    # ---- Start ----

    st.divider()


    if data is not None and st.button(
        "Start Draft!",
        type="primary"
    ):

        players = [
            p.strip()
            for p in players
            if p.strip()
        ]


        if len(players) < 2:
            st.error(
                "Need at least 2 drafters"
            )
            st.stop()


        if len(set(players)) != len(players):
            st.error(
                "Drafter names must be unique"
            )
            st.stop()


        if not selected_leagues:
            st.error(
                "Select at least one league"
            )
            st.stop()


        draft_pool = (
            data[
                data["league"]
                .isin(selected_leagues)
            ]
            .sort_values(
                "prob",
                ascending=False
            )
        )


        if draft_pool.empty:
            st.error(
                "No draftable teams found for the selected leagues"
            )
            st.stop()


        st.session_state.players = players
        st.session_state.snake = snake
        st.session_state.rounds = rounds
        st.session_state.selected_leagues = selected_leagues

        st.session_state.data = draft_pool

        st.session_state.drafts = {
            p: []
            for p in players
        }

        st.session_state.round = 1
        st.session_state.pick = 0

        st.session_state.page = "draft"

        st.rerun()



# ==========================
# DRAFT ROOM
# ==========================

elif st.session_state.page == "draft":

    players = st.session_state.players
    n_players = len(players)


    # Determine current drafter

    if st.session_state.snake:

        if st.session_state.round % 2 == 1:
            player_idx = st.session_state.pick

        else:
            player_idx = (
                n_players
                - 1
                - st.session_state.pick
            )

    else:

        player_idx = st.session_state.pick



    current_player = players[player_idx]


    pick_number = (
        (st.session_state.round - 1)
        * n_players
        + st.session_state.pick
        + 1
    )


    st.title("🏟 Draft Room")


    st.subheader(
        f"Round {st.session_state.round}/{st.session_state.rounds} "
        f"• Pick {pick_number} "
        f"• ⏱ {current_player} is on the clock"
    )


    left, right = st.columns([3, 1])


    # ==========================
    # DRAFT POOL
    # ==========================

    with left:

        st.header("Available Draft Pool")


        # Advanced filters

        with st.expander("🔍 Advanced Filters"):

            c1, c2 = st.columns(2)


            with c1:

                league_filter = st.multiselect(
                    "League",
                    sorted(
                        st.session_state.data["league"]
                        .unique()
                    )
                )


            with c2:

                search = st.text_input(
                    "Search team"
                )


            hide_zero_odds = st.toggle(
                "Hide 0% odds",
                value=True
            )


        pool = st.session_state.data.copy()


        if league_filter:

            pool = pool[
                pool["league"]
                .isin(league_filter)
            ]


        if search:

            pool = pool[
                pool["team"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]


        if hide_zero_odds:

            pool = pool[
                pool["prob"] > 0
            ]



        h1, h2, h3, h4 = st.columns(
            [3, 1, 1, 1]
        )

        h1.markdown("**Team**")
        h2.markdown("**League**")
        h3.markdown("**Win Probability**")
        h4.markdown("**Action**")



        for idx, row in pool.iterrows():

            c1, c2, c3, c4 = st.columns(
                [3, 1, 1, 1]
            )


            c1.write(
                row["team"]
            )


            c2.write(
                row["league"]
            )


            color = prob_color(
                row["prob"]
            )


            c3.markdown(
                f"""
                <span style="
                color:{color};
                font-weight:bold">
                {row['prob']:.1f}%
                </span>
                """,
                unsafe_allow_html=True
            )


            if c4.button(
                "Draft",
                key=f"draft_{idx}"
            ):
                try:
                    prob_at_pick = float(row.get("prob", 0.0))
                except (TypeError, ValueError):
                    prob_at_pick = 0.0

                structured_pick = normalize_pick_entry(
                    {
                        "team": row.get("team", ""),
                        "league": row.get("league", ""),
                        "prob_at_pick": prob_at_pick,
                        "round": st.session_state.round,
                        "pick_in_round": st.session_state.pick + 1,
                        "overall_pick": pick_number,
                    }
                )

                st.session_state.drafts[
                    current_player
                ].append(
                    structured_pick
                )


                st.session_state.data = (
                    st.session_state.data
                    .drop(idx)
                )


                st.session_state.pick += 1


                if (
                    st.session_state.pick
                    >= n_players
                ):

                    st.session_state.pick = 0
                    st.session_state.round += 1



                if (
                    st.session_state.round
                    > st.session_state.rounds
                ):

                    st.session_state.page = "finished"


                st.rerun()



    # ==========================
    # DRAFT BOARD
    # ==========================

    with right:

        st.header("📋 Draft Board")


        for player in players:

            st.markdown(
                f"**{player}**"
            )


            picks = st.session_state.drafts[player]


            if picks:

                for i, selection in enumerate(
                    picks,
                    start=1
                ):
                    pick_team = normalize_pick_entry(selection, overall_pick=i)["team"]

                    st.write(
                        f"{i}. {pick_team}"
                    )

            else:

                st.caption(
                    "No picks yet"
                )


            st.divider()



# ==========================
# FINISHED
# ==========================

elif st.session_state.page == "finished":

    st.title("Draft Complete")


    st.subheader(
        "Final Draft Results (Round Grid)"
    )

    show_odds_in_grid = st.toggle(
        "Show odds in round grid labels",
        value=False,
        key="show_odds_in_round_grid",
    )

    round_grid_results, round_grid_leagues = build_round_grid_dataframe(
        st.session_state.drafts,
        drafter_order=st.session_state.get("players", []),
        include_odds=show_odds_in_grid,
    )

    leagues_in_grid = []
    if not round_grid_leagues.empty:
        for league_name in round_grid_leagues.to_numpy().flatten().tolist():
            league_name = str(league_name).strip()
            if league_name:
                leagues_in_grid.append(league_name)

    league_palette = build_league_color_palette(leagues_in_grid)
    styled_round_grid = style_round_grid(
        round_grid_results,
        round_grid_leagues,
        league_palette,
    )

    st.dataframe(
        styled_round_grid,
        use_container_width=True,
    )

    if league_palette:
        legend_items = "".join(
            [
                (
                    f"<span style=\"display:inline-block;margin:0 10px 8px 0;\">"
                    f"<span style=\"display:inline-block;width:12px;height:12px;"
                    f"border-radius:3px;background:{color};margin-right:6px;"
                    f"vertical-align:middle;border:1px solid #d1d5db;\"></span>"
                    f"{league}</span>"
                )
                for league, color in league_palette.items()
            ]
        )
        st.markdown(legend_items, unsafe_allow_html=True)


    results = create_results_csv(
        st.session_state.drafts
    )


    st.subheader(
        "Flat Draft Results"
    )


    st.dataframe(
        results,
        hide_index=True,
        use_container_width=True
    )


    csv = results.to_csv(
        index=False
    )


    st.download_button(
        label="Download Draft Results",
        data=csv,
        file_name="draft_results.csv",
        mime="text/csv"
    )


    round_grid_csv = round_grid_results.to_csv(index=True)

    st.download_button(
        label="Download Round Grid Results",
        data=round_grid_csv,
        file_name="draft_round_grid_results.csv",
        mime="text/csv"
    )


    st.subheader(
        "Winners and Losers Standings"
    )


    selected_leagues = st.session_state.get(
        "selected_leagues",
        st.session_state.get("league_multiselect", list(LEAGUES.keys()))
    )
    refreshed_probabilities = refresh_selected_league_probabilities(
        selected_leagues
    )
    standings = build_winners_losers_standings(
        st.session_state.drafts,
        refreshed_probabilities
    )

    top_picks_df, top_picks_snapshot = build_top_selections_by_drafter(
        st.session_state.drafts,
        top_n=3,
        drafter_order=st.session_state.get("players", []),
    )
    ownership_matrix_df, ownership_summary_df, ownership_snapshot = build_league_ownership_analytics(
        st.session_state.drafts,
        drafter_order=st.session_state.get("players", []),
    )
    analytics_snapshot = {
        "top_n": 3,
        "top_selections": top_picks_snapshot,
        "league_ownership": ownership_snapshot,
    }

    persistence_message = None
    if not standings.empty and not st.session_state.get("history_snapshot_saved", False):
        try:
            was_saved = persist_completed_draft_snapshot(
                st.session_state.drafts,
                standings,
                analytics=analytics_snapshot,
            )
            st.session_state.history_snapshot_saved = True
            if was_saved:
                persistence_message = "Saved draft snapshot to draft_history.jsonl"
            else:
                persistence_message = "Draft snapshot already exists in draft_history.jsonl"
        except Exception:
            persistence_message = "Unable to persist draft snapshot to draft_history.jsonl"


    if standings.empty:

        st.info(
            "No standings available yet."
        )

    else:

        standings_display = standings.rename(
            columns={
                "rank": "Rank",
                "drafter": "Drafter",
                "picks_count": "Picks",
                "total_win_probability": "Total Win Probability (%)",
                "average_pick_probability": "Average Pick Probability (%)",
            }
        )

        st.dataframe(
            standings_display,
            hide_index=True,
            use_container_width=True
        )

        st.success(
            f"Winner: {standings.iloc[0]['drafter']}"
        )

        if len(standings) > 1:
            st.warning(
                f"Loser: {standings.iloc[-1]['drafter']}"
            )

    st.subheader(
        "Top Selections by Drafter"
    )
    st.caption(
        "Top picks are ranked by pick-time probability captured when each selection was drafted."
    )

    if top_picks_df.empty:
        st.info(
            "No top selections available yet."
        )
    else:
        top_picks_display = top_picks_df.rename(
            columns={
                "drafter": "Drafter",
                "top_pick_rank": "Top Pick",
                "team": "Team",
                "league": "League",
                "prob_at_pick": "Pick-Time Probability (%)",
                "overall_pick": "Overall Pick",
            }
        )

        top_picks_styler = top_picks_display.style.format(
            {"Pick-Time Probability (%)": "{:.1f}%"},
            na_rep="",
        )
        st.dataframe(
            top_picks_styler,
            hide_index=True,
            use_container_width=True,
        )

    st.subheader(
        "League Ownership Matrix"
    )
    st.caption(
        "Each value is the sum of pick-time probabilities by league and drafter."
    )

    if ownership_matrix_df.empty:
        st.info(
            "No ownership matrix available yet."
        )
    else:
        ownership_matrix_styler = ownership_matrix_df.style.format("{:.1f}%")
        st.dataframe(
            ownership_matrix_styler,
            use_container_width=True,
        )

    st.subheader(
        "League Ownership Summary"
    )
    if ownership_summary_df.empty:
        st.info(
            "No ownership summary available yet."
        )
    else:
        ownership_summary_display = ownership_summary_df.rename(
            columns={
                "league": "League",
                "ownership": "Ownership",
                "owners": "Drafter(s)",
                "top_total_prob": "Top Total Probability (%)",
            }
        )
        ownership_summary_styler = ownership_summary_display.style.format(
            {"Top Total Probability (%)": "{:.1f}%"}
        )
        st.dataframe(
            ownership_summary_styler,
            hide_index=True,
            use_container_width=True,
        )

    if persistence_message:
        st.caption(persistence_message)


    st.divider()


    if st.button(
        "Start New Draft"
    ):

        st.session_state.clear()
        st.rerun()
