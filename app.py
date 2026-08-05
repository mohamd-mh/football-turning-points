from pathlib import Path

import streamlit as st

from utils.data_loader import load_csv


st.set_page_config(
    page_title="Football Turning Points",
    page_icon="⚽",
    layout="wide",
)

css_path = Path(__file__).parent / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

league_season = load_csv("02_league_season_metrics.csv")
team_season = load_csv("05_team_season_metrics.csv")
transition_cases = load_csv("08_team_transition_cases.csv")
outlier_cases = load_csv("09_match_outlier_cases.csv")

total_matches = int(league_season["MatchRows"].sum())
total_leagues = int(league_season["League"].nunique())
total_seasons = int(league_season["Season"].nunique())
total_teams = int(team_season["Team"].nunique())
turning_point_matches = int(transition_cases["MatchID"].nunique())
outlier_matches = int(outlier_cases["MatchID"].nunique())

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">INTERACTIVE FOOTBALL ANALYTICS</div>
        <h1>⚽ Football Turning Points</h1>
        <p>
            Explore how matches change between halftime and full time across
            Europe’s five major football leagues.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="research-box">
        <div class="research-label">MAIN RESEARCH QUESTION</div>
        <div class="research-text">
            How do European football teams protect leads, recover from deficits,
            break halftime draws, and experience volatile second halves across
            leagues and seasons?
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Dataset at a glance")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Matches", f"{total_matches:,}")
m2.metric("Leagues", f"{total_leagues}")
m3.metric("Seasons", f"{total_seasons}")
m4.metric("Teams", f"{total_teams}")
m5.metric("Team-season records", f"{len(team_season):,}")

st.subheader("Choose an analysis path")

page1, page2, page3 = st.columns(3)

with page1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">League Overview</div>
            <div class="feature-text">
                Compare leagues and seasons through lead protection, comeback
                ability, scoring, volatility, and halftime-to-full-time transitions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/1_League_Overview.py",
        label="Open League Overview",
        icon="📈",
        use_container_width=True,
    )

with page2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Team Explorer</div>
            <div class="feature-text">
                Examine a club’s development across seasons, compare it with its
                league, and identify differences between home and away performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/2_Team_Explorer.py",
        label="Open Team Explorer",
        icon="🛡️",
        use_container_width=True,
    )

with page3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🔎</div>
            <div class="feature-title">Match Cases</div>
            <div class="feature-text">
                Move from aggregate patterns to individual comebacks, collapses,
                recoveries, breakthroughs, and statistical outliers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/3_Match_Cases.py",
        label="Open Match Cases",
        icon="🔎",
        use_container_width=True,
    )

st.subheader("How to read the analysis")

definition1, definition2, definition3, definition4 = st.columns(4)

with definition1:
    st.markdown(
        """
        <div class="definition-card">
            <div class="definition-title">Lead protection</div>
            <div class="definition-text">
                The percentage of halftime leads that remain wins at full time.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with definition2:
    st.markdown(
        """
        <div class="definition-card">
            <div class="definition-title">Comeback win</div>
            <div class="definition-text">
                A team trails at halftime but finishes the match as the winner.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with definition3:
    st.markdown(
        """
        <div class="definition-card">
            <div class="definition-title">Draw breakthrough</div>
            <div class="definition-text">
                A team is level at halftime and converts the match into a win.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with definition4:
    st.markdown(
        """
        <div class="definition-card">
            <div class="definition-title">Match volatility</div>
            <div class="definition-text">
                The extent to which the score or match state changes after halftime.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Why this visualization is useful")

left, right = st.columns([1.2, 1])

with left:
    st.markdown(
        """
        <div class="content-panel">
            <div class="panel-title">From thousands of rows to interpretable patterns</div>
            <div class="panel-text">
                Manually reviewing match records makes it difficult to compare
                leagues, identify long-term changes, or locate exceptional matches.
                This application links overview, comparison, and case-level views so
                users can move from a general pattern to the matches behind it.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div class="content-panel">
            <div class="panel-title">Analytical depth</div>
            <div class="panel-text">
                The system includes <strong>{turning_point_matches:,}</strong>
                unique turning-point matches and
                <strong>{outlier_matches:,}</strong> unique matches available for
                outlier investigation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(
    "Dataset coverage: 2015/16–2024/25. "
    "Leagues: English Premier League, Spanish La Liga, Italian Serie A, "
    "German Bundesliga, and French Ligue 1."
)