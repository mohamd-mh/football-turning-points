from pathlib import Path

import streamlit as st

from utils.data_loader import load_csv


st.set_page_config(
    page_title="Football Turning Points",
    page_icon="⚽",
    layout="wide",
)

ROOT = Path(__file__).parent
CSS_PATH = ROOT / "assets" / "style.css"


def home_page() -> None:
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .home-definition-card {
            min-height: 122px;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 12px;
            background: rgba(128, 128, 128, 0.035);
        }

        .home-definition-title {
            font-size: 0.92rem;
            font-weight: 750;
            margin-bottom: 0.42rem;
        }

        .home-definition-text {
            font-size: 0.86rem;
            line-height: 1.48;
            opacity: 0.76;
        }

        .home-value-card {
            min-height: 145px;
            padding: 1rem 1.05rem;
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 12px;
            background: rgba(128, 128, 128, 0.035);
        }

        .home-value-title {
            font-size: 0.94rem;
            font-weight: 760;
            margin-bottom: 0.48rem;
        }

        .home-value-text {
            font-size: 0.86rem;
            line-height: 1.52;
            opacity: 0.76;
        }

        .home-footer {
            margin-top: 0.9rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(128, 128, 128, 0.18);
            font-size: 0.78rem;
            line-height: 1.5;
            opacity: 0.58;
        }

        div[data-testid="stPageLink"] {
            margin-top: -0.35rem;
        }
        </style>
        """,
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
                Explore how matches change between halftime and full time
                across Europe’s five major football leagues.
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
                How do European football teams protect leads, recover from
                deficits, break halftime draws, and experience volatile second
                halves across leagues and seasons?
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
                    Compare leagues and seasons through lead protection,
                    comeback ability, scoring, volatility, and
                    halftime-to-full-time transitions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            LEAGUE_PAGE,
            label="Open League Overview",
            icon="📈",
            width="stretch",
        )

    with page2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <div class="feature-title">Team Explorer</div>
                <div class="feature-text">
                    Examine a club’s development across seasons, compare it
                    with its league, and identify differences between home
                    and away performance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            TEAM_PAGE,
            label="Open Team Explorer",
            icon="🛡️",
            width="stretch",
        )

    with page3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🔎</div>
                <div class="feature-title">Match Cases</div>
                <div class="feature-text">
                    Move from aggregate patterns to individual comebacks,
                    collapses, recoveries, breakthroughs, and statistical
                    outliers.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            MATCH_PAGE,
            label="Open Match Cases",
            icon="🔎",
            width="stretch",
        )

    st.subheader("How to read the analysis")
    st.caption("These six terms are used consistently across the dashboards.")

    row1 = st.columns(3)
    row2 = st.columns(3)

    definitions = [
        (
            "Lead protection",
            "The percentage of halftime leads that remain wins at full time.",
        ),
        (
            "Comeback win",
            "A team trails at halftime but finishes the match as the winner.",
        ),
        (
            "Recovery draw",
            "A team trails at halftime but recovers to finish the match level.",
        ),
        (
            "Draw breakthrough",
            "A team is level at halftime and converts the match into a win.",
        ),
        (
            "Lead collapse",
            "A team leads at halftime but finishes the match with a loss.",
        ),
        (
            "Match volatility",
            "The extent to which the score or match state changes after halftime.",
        ),
    ]

    for column, (title, description) in zip(row1 + row2, definitions):
        with column:
            st.markdown(
                f"""
                <div class="home-definition-card">
                    <div class="home-definition-title">{title}</div>
                    <div class="home-definition-text">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("Why this visualization is useful")
    value1, value2, value3 = st.columns(3)

    with value1:
        st.markdown(
            """
            <div class="home-value-card">
                <div class="home-value-title">
                    From thousands of rows to patterns
                </div>
                <div class="home-value-text">
                    Visual comparison makes it possible to identify league,
                    season, and team patterns without manually inspecting
                    thousands of match records.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with value2:
        st.markdown(
            f"""
            <div class="home-value-card">
                <div class="home-value-title">
                    Overview → detail
                </div>
                <div class="home-value-text">
                    The analysis moves from league-level patterns to team
                    behavior and then to individual evidence. The case view
                    reaches <strong>{turning_point_matches:,}</strong> unique
                    turning-point matches, while the outlier explorer ranks
                    the full <strong>{outlier_matches:,}</strong>-match
                    population.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with value3:
        st.markdown(
            """
            <div class="home-value-card">
                <div class="home-value-title">
                    Interactive exploration
                </div>
                <div class="home-value-text">
                    Filters, coordinated views, benchmarks, tooltips, rankings,
                    and details-on-demand let the viewer investigate a pattern
                    instead of only looking at a static summary.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="home-footer">
            <strong>Dataset coverage:</strong> 2015/16–2024/25 ·
            <strong>Leagues:</strong> English Premier League, Spanish La Liga,
            Italian Serie A, German Bundesliga, and French Ligue 1.
        </div>
        """,
        unsafe_allow_html=True,
    )


HOME_PAGE = st.Page(
    home_page,
    title="Home",
    icon="🏠",
    default=True,
)

LEAGUE_PAGE = st.Page(
    "pages/1_League_Overview.py",
    title="League Overview",
    icon="📈",
    url_path="League_Overview",
)

TEAM_PAGE = st.Page(
    "pages/2_Team_Explorer.py",
    title="Team Explorer",
    icon="🛡️",
    url_path="Team_Explorer",
)

MATCH_PAGE = st.Page(
    "pages/3_Match_Cases.py",
    title="Match Cases",
    icon="🔎",
    url_path="Match_Cases",
)

navigation = st.navigation(
    [
        HOME_PAGE,
        LEAGUE_PAGE,
        TEAM_PAGE,
        MATCH_PAGE,
    ],
    position="sidebar",
    expanded=True,
)

navigation.run()