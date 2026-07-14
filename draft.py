import streamlit as st
import pandas as pd
import requests


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


def create_results_csv(drafts):
    rows = []

    for player, teams in drafts.items():
        for pick, team in enumerate(teams, start=1):
            rows.append({
                "Drafter": player,
                "Pick": pick,
                "Team": team
            })

    return pd.DataFrame(rows)


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

def get_event(event_ticker):

    event_ticker = event_ticker.upper().strip()

    url = f"https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker={event_ticker}"
    response = requests.get(url)

    teams = []
    probs = []

    for market in response.json()['markets']:

        team = market["yes_sub_title"].strip()
        teams.append(team)

        ask_price = float(market["previous_yes_ask_dollars"])
        bid_price = float(market["previous_yes_bid_dollars"])
        prob = 100 * (ask_price + bid_price) / 2 if (ask_price > 0 and bid_price > 0) else 0
        probs.append(prob)

    df = pd.DataFrame(
        {
            "team": teams,
            "prob": probs
        }
    )
    df["prob"] = 100 * df["prob"] / df["prob"].sum()

    return df


LEAGUES = {
    "US Open Men": "kxatp-26uso",
    "US Open Women": "kxwta-26uso",
    "College Football": "kxncaaf-27",
    "Premier League": "kxpremierleague-27",
}

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
        import time
        time.sleep(2)  # Simulate a delay for fetching data
        data = pd.DataFrame()
        for league_name in selected_leagues:
            league_ticker = LEAGUES[league_name]
            league_events = get_event(league_ticker)
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


        st.session_state.players = players
        st.session_state.snake = snake
        st.session_state.rounds = rounds

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

                st.session_state.drafts[
                    current_player
                ].append(
                    row["team"]
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

                for i, team in enumerate(
                    picks,
                    start=1
                ):

                    st.write(
                        f"{i}. {team}"
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


    results = create_results_csv(
        st.session_state.drafts
    )


    st.subheader(
        "Final Draft Results"
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


    st.divider()


    if st.button(
        "Start New Draft"
    ):

        st.session_state.clear()
        st.rerun()