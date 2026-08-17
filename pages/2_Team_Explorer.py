from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_csv


# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Team Explorer",
    page_icon="🛡️",
    layout="wide",
)

css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

# Page-specific refinements.
st.markdown(
    """
    <style>
    .team-profile-banner {
        padding: 0.9rem 1rem;
        border-left: 4px solid #7CB9E8;
        border-radius: 10px;
        background: rgba(124, 185, 232, 0.07);
        margin-bottom: 1rem;
    }

    .team-profile-title {
        font-weight: 800;
        font-size: 1.02rem;
        margin-bottom: 0.25rem;
    }

    .team-profile-text {
        opacity: 0.82;
        line-height: 1.45;
    }

    .team-insight-card {
        padding: 0.95rem 1.05rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
        background: rgba(128, 128, 128, 0.035);
        margin-top: 0.5rem;
    }

    .team-insight-label {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.04rem;
        text-transform: uppercase;
        opacity: 0.62;
        margin-bottom: 0.3rem;
    }

    .team-insight-text {
        font-size: 0.98rem;
        font-weight: 650;
        line-height: 1.5;
    }

    .tab-guidance {
        margin-top: -0.25rem;
        margin-bottom: 0.65rem;
        opacity: 0.72;
        font-size: 0.88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------
team_season = load_csv("05_team_season_metrics.csv")
team_overall = load_csv("04_team_metrics.csv")
home_away = load_csv("06_home_away_metrics.csv")

LEAGUE_COLORS = {
    "English Premier League": "#7CB9E8",
    "Spanish La Liga": "#FF5A5F",
    "Italian Serie A": "#4D96FF",
    "German Bundesliga": "#F4A261",
    "French Ligue 1": "#5CD6A0",
}

HOME_COLOR = "#7CB9E8"
AWAY_COLOR = "#F4A261"
PEER_COLOR = "#7C8493"
BENCHMARK_COLOR = "#A0A6B1"


# ---------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------
PERFORMANCE_METRICS = {
    "Points per match": {
        "numerator": "Points",
        "denominator": "TeamMatchRows",
        "ylabel": "Points per match",
        "decimals": 2,
        "range_floor": 0.0,
        "minimum_upper": 3.0,
        "interpretation": "Higher values indicate better results.",
    },
    "Goals scored per match": {
        "numerator": "GoalsFor",
        "denominator": "TeamMatchRows",
        "ylabel": "Goals scored per match",
        "decimals": 2,
        "range_floor": 0.0,
        "minimum_upper": 3.0,
        "interpretation": "Higher values indicate more scoring.",
    },
    "Goals conceded per match": {
        "numerator": "GoalsAgainst",
        "denominator": "TeamMatchRows",
        "ylabel": "Goals conceded per match",
        "decimals": 2,
        "range_floor": 0.0,
        "minimum_upper": 3.0,
        "interpretation": "Lower values indicate better defensive performance.",
    },
}

TRANSITION_METRICS = {
    "Lead protection rate": {
        "numerator": ["ProtectedLeads"],
        "denominator": "LeadOpportunities",
        "ylabel": "Lead protection rate (%)",
        "description": (
            "Percentage of halftime leads that were still wins at full time. "
            "Higher values indicate stronger lead protection."
        ),
    },
    "Comeback win rate": {
        "numerator": ["ComebackWins"],
        "denominator": "BehindOpportunities",
        "ylabel": "Comeback win rate (%)",
        "description": (
            "Percentage of halftime deficits converted into full-time wins. "
            "Higher values indicate stronger comeback performance."
        ),
    },
    "Recovery rate": {
        "numerator": ["ComebackWins", "RecoveryDraws"],
        "denominator": "BehindOpportunities",
        "ylabel": "Recovery rate (%)",
        "description": (
            "Percentage of halftime deficits converted into either a draw or a win. "
            "Higher values indicate stronger recovery performance."
        ),
    },
    "Draw breakthrough rate": {
        "numerator": ["DrawBreakthroughs"],
        "denominator": "LevelOpportunities",
        "ylabel": "Draw breakthrough rate (%)",
        "description": (
            "Percentage of halftime draws converted into full-time wins. "
            "Higher values indicate stronger draw-breakthrough performance."
        ),
    },
    "State-change rate": {
        "numerator": ["StateChanges"],
        "denominator": "TeamMatchRows",
        "ylabel": "State-change rate (%)",
        "description": (
            "Percentage of team-match states that changed after halftime. "
            "This measures change frequency and is not inherently better or worse."
        ),
    },
    "Lead-collapse rate": {
        "numerator": ["LeadCollapses"],
        "denominator": "LeadOpportunities",
        "ylabel": "Lead-collapse rate (%)",
        "description": (
            "Percentage of halftime leads that became full-time losses. "
            "Lower values indicate better lead retention."
        ),
    },
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def safe_ratio_from_sums(
    frame: pd.DataFrame,
    numerators: list[str],
    denominator: str,
    multiplier: float = 1.0,
) -> float:
    denominator_sum = float(frame[denominator].sum())
    if denominator_sum == 0:
        return float("nan")

    numerator_sum = sum(float(frame[column].sum()) for column in numerators)
    return numerator_sum / denominator_sum * multiplier


def ratio_per_row(
    frame: pd.DataFrame,
    numerators: list[str],
    denominator: str,
    multiplier: float = 1.0,
) -> pd.Series:
    numerator = sum(frame[column].astype(float) for column in numerators)
    denominator_values = (
        frame[denominator]
        .astype(float)
        .replace(0, float("nan"))
    )

    return numerator / denominator_values * multiplier


def weighted_league_benchmark(
    frame: pd.DataFrame,
    numerators: list[str],
    denominator: str,
    multiplier: float = 1.0,
) -> float:
    return safe_ratio_from_sums(
        frame,
        numerators,
        denominator,
        multiplier,
    )


def profile_context_sentence(
    lead_value: float,
    comeback_value: float,
    lead_benchmark: float,
    comeback_benchmark: float,
    eligible: bool,
) -> str:
    if not eligible:
        return (
            "The profile is marked as a small sample; interpret the league "
            "comparison cautiously."
        )

    lead_above = lead_value >= lead_benchmark
    comeback_above = comeback_value >= comeback_benchmark

    if lead_above and comeback_above:
        return (
            "Above the eligible-peer league benchmark in both lead protection "
            "and comeback-win rate."
        )

    if lead_above and not comeback_above:
        return (
            "Above the eligible-peer league benchmark in lead protection, "
            "but below it in comeback-win rate."
        )

    if not lead_above and comeback_above:
        return (
            "Above the eligible-peer league benchmark in comeback-win rate, "
            "but below it in lead protection."
        )

    return (
        "Below the eligible-peer league benchmark in both lead protection "
        "and comeback-win rate."
    )


def add_quadrant_annotations(
    fig: go.Figure,
    x_low: float,
    x_high: float,
    y_low: float,
    y_high: float,
    x_benchmark: float,
    y_benchmark: float,
) -> None:
    annotations = [
        (
            (x_benchmark + x_high) / 2,
            (y_benchmark + y_high) / 2,
            "Above both",
        ),
        (
            (x_benchmark + x_high) / 2,
            (y_low + y_benchmark) / 2,
            "Stronger lead protection",
        ),
        (
            (x_low + x_benchmark) / 2,
            (y_benchmark + y_high) / 2,
            "Stronger comeback",
        ),
        (
            (x_low + x_benchmark) / 2,
            (y_low + y_benchmark) / 2,
            "Below both",
        ),
    ]

    for x_pos, y_pos, label in annotations:
        fig.add_annotation(
            x=x_pos,
            y=y_pos,
            text=label,
            showarrow=False,
            font=dict(
                size=10,
                color="rgba(200,205,215,0.68)",
            ),
        )


def make_dumbbell_chart(
    venue_frame: pd.DataFrame,
    metric_definitions: list[dict],
    percentage_mode: bool,
) -> go.Figure:
    home_row = venue_frame[venue_frame["Venue"] == "Home"]
    away_row = venue_frame[venue_frame["Venue"] == "Away"]

    if home_row.empty or away_row.empty:
        return go.Figure()

    labels = [definition["label"] for definition in metric_definitions]
    y_positions = list(range(len(labels)))

    home_values = [
        float(home_row[definition["column"]].iloc[0])
        for definition in metric_definitions
    ]
    away_values = [
        float(away_row[definition["column"]].iloc[0])
        for definition in metric_definitions
    ]

    fig = go.Figure()

    for y_pos, home_value, away_value in zip(
        y_positions,
        home_values,
        away_values,
    ):
        fig.add_shape(
            type="line",
            x0=min(home_value, away_value),
            x1=max(home_value, away_value),
            y0=y_pos,
            y1=y_pos,
            line=dict(
                color="rgba(160,166,177,0.42)",
                width=3,
            ),
            layer="below",
        )

    decimals = 1 if percentage_mode else 2
    suffix = "%" if percentage_mode else ""

    # Slight vertical offsets keep equal Home/Away values visible as
    # two distinct observations instead of one marker hiding the other.
    home_y = [position - 0.07 for position in y_positions]
    away_y = [position + 0.07 for position in y_positions]

    home_text_positions = []
    away_text_positions = []

    for home_value, away_value in zip(home_values, away_values):
        if percentage_mode:
            near_left_edge = min(home_value, away_value) <= 4.0
            nearly_equal = abs(home_value - away_value) <= 3.0
        else:
            near_left_edge = min(home_value, away_value) <= 0.15
            nearly_equal = abs(home_value - away_value) <= 0.10

        if near_left_edge and nearly_equal:
            home_text_positions.append("top right")
            away_text_positions.append("bottom right")
        else:
            home_text_positions.append("top center")
            away_text_positions.append("bottom center")

    fig.add_trace(
        go.Scatter(
            x=home_values,
            y=home_y,
            mode="markers+text",
            name="Home",
            marker=dict(
                size=16,
                color=HOME_COLOR,
                line=dict(color="white", width=1),
            ),
            text=[
                f"{value:.{decimals}f}{suffix}"
                for value in home_values
            ],
            textposition=home_text_positions,
            cliponaxis=False,
            hovertemplate=(
                "<b>Home</b><br>"
                "%{text}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=away_values,
            y=away_y,
            mode="markers+text",
            name="Away",
            marker=dict(
                size=16,
                color=AWAY_COLOR,
                line=dict(color="white", width=1),
            ),
            text=[
                f"{value:.{decimals}f}{suffix}"
                for value in away_values
            ],
            textposition=away_text_positions,
            cliponaxis=False,
            hovertemplate=(
                "<b>Away</b><br>"
                "%{text}"
                "<extra></extra>"
            ),
        )
    )

    if percentage_mode:
        x_range = [0, 100]
        x_title = "Rate (%)"
    else:
        maximum = max(home_values + away_values)
        x_range = [0, max(3.0, maximum * 1.18)]
        x_title = "Per-match value"

    fig.update_layout(
        height=420,
        margin=dict(l=35, r=30, t=25, b=20),
        xaxis=dict(
            title=x_title,
            range=x_range,
            zeroline=False,
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=y_positions,
            ticktext=labels,
            range=[len(labels) - 0.45, -0.45],
            title="",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            title="",
        ),
    )

    if percentage_mode:
        fig.update_xaxes(ticksuffix="%")

    return fig


# ---------------------------------------------------------------------
# Header + filters
# ---------------------------------------------------------------------
st.title("🛡️ Team Performance Explorer")
st.caption(
    "Compare a club with its league, follow its development across seasons, "
    "and examine how venue changes performance."
)

leagues = sorted(team_season["League"].dropna().unique())

with st.sidebar:
    st.header("Team selection")

    selected_league = st.selectbox(
        "League",
        leagues,
        key="team_explorer_league",
    )

    available_teams = sorted(
        team_season.loc[
            team_season["League"] == selected_league,
            "Team",
        ]
        .dropna()
        .unique()
    )

    selected_team = st.selectbox(
        "Team",
        available_teams,
        key="team_explorer_team",
    )

    st.divider()
    st.caption(
        "All comparisons update together for the selected club."
    )


selected_seasons = team_season[
    (team_season["League"] == selected_league)
    & (team_season["Team"] == selected_team)
].copy()

selected_overall = team_overall[
    (team_overall["League"] == selected_league)
    & (team_overall["Team"] == selected_team)
].copy()

venue = home_away[
    (home_away["League"] == selected_league)
    & (home_away["Team"] == selected_team)
].copy()

if selected_seasons.empty or selected_overall.empty:
    st.warning("No data is available for this team.")
    st.stop()

season_order = sorted(
    team_season["Season"].dropna().astype(str).unique()
)

selected_seasons["Season"] = pd.Categorical(
    selected_seasons["Season"].astype(str),
    categories=season_order,
    ordered=True,
)
selected_seasons = selected_seasons.sort_values("Season")

overall_row = selected_overall.iloc[0]


# ---------------------------------------------------------------------
# League peer benchmarks used by the banner + scatterplot
# ---------------------------------------------------------------------
league_teams = team_overall[
    team_overall["League"] == selected_league
].copy()

eligible_peers = league_teams[
    league_teams["QuadrantEligible"] == 1
].copy()

if eligible_peers.empty:
    eligible_peers = league_teams.copy()

lead_benchmark = weighted_league_benchmark(
    eligible_peers,
    ["ProtectedLeads"],
    "LeadOpportunities",
    100,
)
comeback_benchmark = weighted_league_benchmark(
    eligible_peers,
    ["ComebackWins"],
    "BehindOpportunities",
    100,
)

profile_name = str(overall_row["TeamProfileQuadrant"])
quadrant_eligible = bool(int(overall_row["QuadrantEligible"]))

profile_sentence = profile_context_sentence(
    float(overall_row["LeadShieldPct"]),
    float(overall_row["ComebackWinRatePct"]),
    lead_benchmark,
    comeback_benchmark,
    quadrant_eligible,
)

st.markdown(
    f"""
    <div class="team-profile-banner">
        <div class="team-profile-title">
            {selected_team} — Profile: {profile_name}
        </div>
        <div class="team-profile-text">
            {profile_sentence}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# KPI snapshot
# ---------------------------------------------------------------------
st.subheader("Team snapshot")

points_per_match = safe_ratio_from_sums(
    selected_seasons,
    ["Points"],
    "TeamMatchRows",
)
goals_scored_per_match = safe_ratio_from_sums(
    selected_seasons,
    ["GoalsFor"],
    "TeamMatchRows",
)
cumulative_goal_difference = int(
    selected_seasons["GoalsFor"].sum()
    - selected_seasons["GoalsAgainst"].sum()
)
lead_protection = safe_ratio_from_sums(
    selected_seasons,
    ["ProtectedLeads"],
    "LeadOpportunities",
    100,
)
comeback_rate = safe_ratio_from_sums(
    selected_seasons,
    ["ComebackWins"],
    "BehindOpportunities",
    100,
)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Points per match", f"{points_per_match:.2f}")
kpi2.metric("Goals scored per match", f"{goals_scored_per_match:.2f}")
kpi3.metric(
    "Cumulative goal difference",
    f"{cumulative_goal_difference:+,}",
)
kpi4.metric("Lead protection rate", f"{lead_protection:.1f}%")
kpi5.metric("Comeback win rate", f"{comeback_rate:.1f}%")


# ---------------------------------------------------------------------
# Compact analytical tabs
# ---------------------------------------------------------------------
season_tab, comparison_tab = st.tabs(
    ["Season trends", "League & venue comparison"]
)


# =====================================================================
# TAB 1 — Season trends
# =====================================================================
with season_tab:
    st.markdown(
        '<div class="tab-guidance">'
        "Use the two selectors to compare long-term results and match-state "
        "behavior without adding separate charts for every metric."
        "</div>",
        unsafe_allow_html=True,
    )

    trend_left, trend_right = st.columns(2)

    # -----------------------------------------------------------------
    # Team vs league performance
    # -----------------------------------------------------------------
    with trend_left:
        st.subheader("How has the team performed relative to its league?")

        performance_metric_name = st.selectbox(
            "Performance measure",
            list(PERFORMANCE_METRICS.keys()),
            key="team_performance_metric",
        )

        performance_config = PERFORMANCE_METRICS[
            performance_metric_name
        ]

        st.caption(performance_config["interpretation"])

        team_performance = selected_seasons[
            ["Season"]
        ].copy()

        team_performance["Selected team"] = ratio_per_row(
            selected_seasons,
            [performance_config["numerator"]],
            performance_config["denominator"],
        )

        league_season_source = team_season[
            team_season["League"] == selected_league
        ].copy()

        league_performance_rows = []
        for season, group in league_season_source.groupby("Season"):
            league_performance_rows.append(
                {
                    "Season": str(season),
                    "League average": safe_ratio_from_sums(
                        group,
                        [performance_config["numerator"]],
                        performance_config["denominator"],
                    ),
                }
            )

        league_performance = pd.DataFrame(
            league_performance_rows
        )

        team_performance["Season"] = (
            team_performance["Season"].astype(str)
        )

        performance_plot = team_performance.merge(
            league_performance,
            on="Season",
            how="left",
        )

        performance_plot["Season"] = pd.Categorical(
            performance_plot["Season"],
            categories=season_order,
            ordered=True,
        )
        performance_plot = performance_plot.sort_values("Season")

        performance_chart = go.Figure()

        performance_chart.add_trace(
            go.Scatter(
                x=performance_plot["Season"],
                y=performance_plot["Selected team"],
                mode="lines+markers",
                name=selected_team,
                line=dict(
                    color=LEAGUE_COLORS.get(
                        selected_league,
                        "#7CB9E8",
                    ),
                    width=3.5,
                ),
                marker=dict(size=8),
                hovertemplate=(
                    f"<b>{selected_team}</b><br>"
                    "Season: %{x}<br>"
                    f"{performance_metric_name}: %{{y:.2f}}"
                    "<extra></extra>"
                ),
            )
        )

        performance_chart.add_trace(
            go.Scatter(
                x=performance_plot["Season"],
                y=performance_plot["League average"],
                mode="lines+markers",
                name="League average",
                line=dict(
                    color=BENCHMARK_COLOR,
                    width=2.5,
                    dash="dash",
                ),
                marker=dict(size=6),
                hovertemplate=(
                    "<b>League average</b><br>"
                    "Season: %{x}<br>"
                    f"{performance_metric_name}: %{{y:.2f}}"
                    "<extra></extra>"
                ),
            )
        )

        candidate_maxima = [
            performance_plot["Selected team"].max(),
            performance_plot["League average"].max(),
        ]
        valid_maxima = [
            float(value)
            for value in candidate_maxima
            if pd.notna(value)
        ]
        observed_max = max(valid_maxima) if valid_maxima else 0.0

        y_upper = max(
            performance_config["minimum_upper"],
            observed_max * 1.12,
        )

        performance_chart.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(
                title=performance_config["ylabel"],
                range=[
                    performance_config["range_floor"],
                    y_upper,
                ],
            ),
            xaxis_title="Season",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.03,
                xanchor="right",
                x=1,
                title="",
            ),
            hovermode="x unified",
        )

        st.plotly_chart(
            performance_chart,
            width="stretch",
            config={"displayModeBar": False},
        )

    # -----------------------------------------------------------------
    # Match-state trend
    # -----------------------------------------------------------------
    with trend_right:
        st.subheader("How has the team's match-state behavior changed?")

        transition_metric_name = st.selectbox(
            "Match-state measure",
            list(TRANSITION_METRICS.keys()),
            key="team_transition_metric",
        )

        transition_config = TRANSITION_METRICS[
            transition_metric_name
        ]

        st.caption(transition_config["description"])

        team_transition = selected_seasons[
            ["Season"]
        ].copy()

        team_transition["Selected team"] = ratio_per_row(
            selected_seasons,
            transition_config["numerator"],
            transition_config["denominator"],
            100,
        )

        league_transition_rows = []
        for season, group in league_season_source.groupby("Season"):
            league_transition_rows.append(
                {
                    "Season": str(season),
                    "League average": safe_ratio_from_sums(
                        group,
                        transition_config["numerator"],
                        transition_config["denominator"],
                        100,
                    ),
                }
            )

        league_transition = pd.DataFrame(
            league_transition_rows
        )

        team_transition["Season"] = (
            team_transition["Season"].astype(str)
        )

        transition_plot = team_transition.merge(
            league_transition,
            on="Season",
            how="left",
        )

        transition_plot["Season"] = pd.Categorical(
            transition_plot["Season"],
            categories=season_order,
            ordered=True,
        )
        transition_plot = transition_plot.sort_values("Season")

        transition_chart = go.Figure()

        transition_chart.add_trace(
            go.Scatter(
                x=transition_plot["Season"],
                y=transition_plot["Selected team"],
                mode="lines+markers",
                name=selected_team,
                line=dict(
                    color=LEAGUE_COLORS.get(
                        selected_league,
                        "#7CB9E8",
                    ),
                    width=3.5,
                ),
                marker=dict(size=8),
                hovertemplate=(
                    f"<b>{selected_team}</b><br>"
                    "Season: %{x}<br>"
                    f"{transition_metric_name}: %{{y:.1f}}%"
                    "<extra></extra>"
                ),
            )
        )

        transition_chart.add_trace(
            go.Scatter(
                x=transition_plot["Season"],
                y=transition_plot["League average"],
                mode="lines+markers",
                name="League average",
                line=dict(
                    color=BENCHMARK_COLOR,
                    width=2.5,
                    dash="dash",
                ),
                marker=dict(size=6),
                hovertemplate=(
                    "<b>League average</b><br>"
                    "Season: %{x}<br>"
                    f"{transition_metric_name}: %{{y:.1f}}%"
                    "<extra></extra>"
                ),
            )
        )

        transition_chart.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Season",
            yaxis=dict(
                title=transition_config["ylabel"],
                range=[0, 100],
                ticksuffix="%",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.03,
                xanchor="right",
                x=1,
                title="",
            ),
            hovermode="x unified",
        )

        st.plotly_chart(
            transition_chart,
            width="stretch",
            config={"displayModeBar": False},
        )


# =====================================================================
# TAB 2 — League & venue comparison
# =====================================================================
with comparison_tab:
    st.markdown(
        '<div class="tab-guidance">'
        "The peer view compares the selected team with eligible clubs in its "
        "league; the venue view compares the same team's home and away values."
        "</div>",
        unsafe_allow_html=True,
    )

    comparison_left, comparison_right = st.columns([1.08, 1])

    # -----------------------------------------------------------------
    # League peer scatterplot
    # -----------------------------------------------------------------
    with comparison_left:
        st.subheader("Where does the team sit within its league?")

        st.caption(
            "Gray dots represent eligible peer teams; the highlighted point "
            "is the selected club. Dashed lines are weighted league benchmarks."
        )

        peers = eligible_peers[
            eligible_peers["Team"] != selected_team
        ].copy()

        scatter_source = pd.concat(
            [
                peers[
                    [
                        "LeadShieldPct",
                        "ComebackWinRatePct",
                    ]
                ],
                selected_overall[
                    [
                        "LeadShieldPct",
                        "ComebackWinRatePct",
                    ]
                ],
            ],
            ignore_index=True,
        )

        x_min_data = float(scatter_source["LeadShieldPct"].min())
        x_max_data = float(scatter_source["LeadShieldPct"].max())
        y_min_data = float(scatter_source["ComebackWinRatePct"].min())
        y_max_data = float(scatter_source["ComebackWinRatePct"].max())

        x_low = max(
            0.0,
            min(x_min_data, lead_benchmark) - 5.0,
        )
        x_high = min(
            100.0,
            max(x_max_data, lead_benchmark) + 5.0,
        )
        y_low = max(
            0.0,
            min(y_min_data, comeback_benchmark) - 3.0,
        )
        y_high = min(
            100.0,
            max(y_max_data, comeback_benchmark) + 3.0,
        )

        quadrant_chart = go.Figure()

        quadrant_chart.add_trace(
            go.Scatter(
                x=peers["LeadShieldPct"],
                y=peers["ComebackWinRatePct"],
                mode="markers",
                name="Eligible peers",
                text=peers["Team"],
                customdata=peers[
                    [
                        "PointsPerMatch",
                        "TeamMatchRows",
                        "TeamProfileQuadrant",
                    ]
                ],
                marker=dict(
                    size=11,
                    color=PEER_COLOR,
                    opacity=0.52,
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Lead protection: %{x:.1f}%<br>"
                    "Comeback win rate: %{y:.1f}%<br>"
                    "Points per match: %{customdata[0]:.2f}<br>"
                    "Team-match rows: %{customdata[1]:.0f}<br>"
                    "Profile: %{customdata[2]}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

        selected_marker_symbol = (
            "circle"
            if quadrant_eligible
            else "diamond-open"
        )

        quadrant_chart.add_trace(
            go.Scatter(
                x=[float(overall_row["LeadShieldPct"])],
                y=[float(overall_row["ComebackWinRatePct"])],
                mode="markers+text",
                name=selected_team,
                text=[selected_team],
                textposition="top center",
                marker=dict(
                    size=19,
                    color=LEAGUE_COLORS.get(
                        selected_league,
                        "#7CB9E8",
                    ),
                    symbol=selected_marker_symbol,
                    line=dict(
                        width=2,
                        color="white",
                    ),
                ),
                hovertemplate=(
                    f"<b>{selected_team}</b><br>"
                    "Lead protection: %{x:.1f}%<br>"
                    "Comeback win rate: %{y:.1f}%<br>"
                    f"Profile: {profile_name}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

        quadrant_chart.add_vline(
            x=lead_benchmark,
            line_dash="dash",
            line_color=BENCHMARK_COLOR,
            line_width=1.4,
        )

        quadrant_chart.add_hline(
            y=comeback_benchmark,
            line_dash="dash",
            line_color=BENCHMARK_COLOR,
            line_width=1.4,
        )

        add_quadrant_annotations(
            quadrant_chart,
            x_low,
            x_high,
            y_low,
            y_high,
            lead_benchmark,
            comeback_benchmark,
        )

        quadrant_chart.update_layout(
            height=460,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(
                title="Lead protection rate (%)",
                range=[x_low, x_high],
                ticksuffix="%",
            ),
            yaxis=dict(
                title="Comeback win rate (%)",
                range=[y_low, y_high],
                ticksuffix="%",
            ),
        )

        st.plotly_chart(
            quadrant_chart,
            width="stretch",
            config={"displayModeBar": False},
        )

        if not quadrant_eligible:
            st.caption(
                "◇ The selected team is shown with an open diamond because "
                "its profile classification is marked as a small sample."
            )

    # -----------------------------------------------------------------
    # Venue comparison
    # -----------------------------------------------------------------
    with comparison_right:
        st.subheader("Does venue matter?")

        venue_group = st.selectbox(
            "Venue comparison",
            [
                "Results & scoring",
                "Match-state performance",
            ],
            key="team_venue_group",
        )

        if venue_group == "Results & scoring":
            venue_definitions = [
                {
                    "label": "Points per match",
                    "column": "PointsPerMatch",
                },
                {
                    "label": "Goals scored per match",
                    "column": "GoalsForPerMatch",
                },
                {
                    "label": "Goals conceded per match",
                    "column": "GoalsAgainstPerMatch",
                },
            ]
            venue_chart = make_dumbbell_chart(
                venue,
                venue_definitions,
                percentage_mode=False,
            )
            st.caption(
                "Connected dots emphasize the gap between home and away "
                "performance on the same per-match scale."
            )
        else:
            venue_definitions = [
                {
                    "label": "Lead protection rate",
                    "column": "LeadShieldPct",
                },
                {
                    "label": "Comeback win rate",
                    "column": "ComebackWinRatePct",
                },
                {
                    "label": "Draw breakthrough rate",
                    "column": "DrawBreakthroughRatePct",
                },
            ]
            venue_chart = make_dumbbell_chart(
                venue,
                venue_definitions,
                percentage_mode=True,
            )
            st.caption(
                "All match-state measures are percentages and therefore share "
                "a common 0–100% scale."
            )

        st.plotly_chart(
            venue_chart,
            width="stretch",
            config={"displayModeBar": False},
        )

    # -----------------------------------------------------------------
    # Quiet automatic insight
    # -----------------------------------------------------------------
    home_row = venue[venue["Venue"] == "Home"]
    away_row = venue[venue["Venue"] == "Away"]

    if not home_row.empty and not away_row.empty:
        home_ppm = float(home_row["PointsPerMatch"].iloc[0])
        away_ppm = float(away_row["PointsPerMatch"].iloc[0])
        home_lead = float(home_row["LeadShieldPct"].iloc[0])
        away_lead = float(away_row["LeadShieldPct"].iloc[0])

        ppm_gap = home_ppm - away_ppm

        if abs(ppm_gap) < 0.01:
            venue_sentence = (
                f"{selected_team} earns essentially the same number of "
                "points per match at home and away."
            )
        elif ppm_gap > 0:
            venue_sentence = (
                f"{selected_team} earns {abs(ppm_gap):.2f} more points per "
                "match at home than away."
            )
        else:
            venue_sentence = (
                f"{selected_team} earns {abs(ppm_gap):.2f} more points per "
                "match away than at home."
            )

        st.markdown(
            f"""
            <div class="team-insight-card">
                <div class="team-insight-label">Venue insight</div>
                <div class="team-insight-text">
                    {venue_sentence}
                    Lead protection is {home_lead:.1f}% at home versus
                    {away_lead:.1f}% away.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )