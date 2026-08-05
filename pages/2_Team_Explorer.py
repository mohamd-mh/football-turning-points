from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_csv


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

PROFILE_DESCRIPTIONS = {
    "Complete Competitors": (
        "Strong at protecting leads and comparatively capable of recovering "
        "from halftime deficits."
    ),
    "Reliable Closers": (
        "Above-average at protecting halftime leads, but less successful when "
        "forced to chase a match."
    ),
    "Resilient Chasers": (
        "Comparatively strong at recovering from deficits, but less reliable "
        "when defending halftime leads."
    ),
    "Vulnerable Teams": (
        "Below the league benchmark in both lead protection and comeback ability."
    ),
}

PERCENTAGE_METRICS = {
    "Lead protection": "LeadShieldPct",
    "Comeback win rate": "ComebackWinRatePct",
    "Recovery rate": "ResilienceRatePct",
    "Draw breakthrough rate": "DrawBreakthroughRatePct",
    "State-change rate": "StateChangeRatePct",
    "Lead-collapse rate": "LeadCollapsePct",
}


def safe_rate(frame: pd.DataFrame, numerator: str, denominator: str) -> float:
    denominator_sum = frame[denominator].sum()
    if denominator_sum == 0:
        return 0.0
    return float(frame[numerator].sum() / denominator_sum * 100)


def safe_ratio(frame: pd.DataFrame, numerator: str, denominator: str) -> float:
    denominator_sum = frame[denominator].sum()
    if denominator_sum == 0:
        return 0.0
    return float(frame[numerator].sum() / denominator_sum)


st.title("🛡️ Team Performance Explorer")
st.caption(
    "Explore how a club protects leads, responds to deficits, scores, "
    "and performs at home and away."
)

leagues = sorted(team_season["League"].dropna().unique())

with st.sidebar:
    st.header("Team selection")

    selected_league = st.selectbox(
        "League",
        leagues,
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
    )

    st.divider()
    st.caption(
        "The team is compared with every club in the selected league."
    )

selected_seasons = team_season[
    (team_season["League"] == selected_league)
    & (team_season["Team"] == selected_team)
].copy()

season_order = sorted(
    team_season["Season"].dropna().astype(str).unique()
)

selected_seasons["Season"] = pd.Categorical(
    selected_seasons["Season"].astype(str),
    categories=season_order,
    ordered=True,
)
selected_seasons = selected_seasons.sort_values("Season")

selected_overall = team_overall[
    (team_overall["League"] == selected_league)
    & (team_overall["Team"] == selected_team)
].copy()

if selected_seasons.empty or selected_overall.empty:
    st.warning("No data is available for this team.")
    st.stop()

overall_row = selected_overall.iloc[0]

points_per_match = safe_ratio(
    selected_seasons,
    "Points",
    "TeamMatchRows",
)
goals_for_per_match = safe_ratio(
    selected_seasons,
    "GoalsFor",
    "TeamMatchRows",
)
lead_protection = safe_rate(
    selected_seasons,
    "ProtectedLeads",
    "LeadOpportunities",
)
comeback_rate = safe_rate(
    selected_seasons,
    "ComebackWins",
    "BehindOpportunities",
)
goal_difference = (
    selected_seasons["GoalsFor"].sum()
    - selected_seasons["GoalsAgainst"].sum()
)

profile = str(overall_row["TeamProfileQuadrant"])
profile_description = PROFILE_DESCRIPTIONS.get(
    profile,
    "A profile based on lead protection and comeback performance.",
)

st.markdown(
    f"""
    <div class="section-note">
        <strong>{selected_team} — {profile}</strong><br>
        {profile_description}
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Team snapshot")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Points per match", f"{points_per_match:.2f}")
kpi2.metric("Goals per match", f"{goals_for_per_match:.2f}")
kpi3.metric("Goal difference", f"{goal_difference:+,.0f}")
kpi4.metric("Lead protection", f"{lead_protection:.1f}%")
kpi5.metric("Comeback wins", f"{comeback_rate:.1f}%")

trend_left, trend_right = st.columns([1.15, 1])

with trend_left:
    st.subheader("League points trend")

    selected_points = selected_seasons[
        ["Season", "PointsPerMatch"]
    ].copy()
    selected_points["Series"] = selected_team

    league_points = (
        team_season[
            team_season["League"] == selected_league
        ]
        .groupby("Season", as_index=False)
        .agg(
            Points=("Points", "sum"),
            Matches=("TeamMatchRows", "sum"),
        )
    )
    league_points["PointsPerMatch"] = (
        league_points["Points"] / league_points["Matches"]
    )
    league_points["Season"] = pd.Categorical(
        league_points["Season"].astype(str),
        categories=season_order,
        ordered=True,
    )
    league_points["Series"] = "League average"

    points_trend = pd.concat(
        [
            selected_points[["Season", "PointsPerMatch", "Series"]],
            league_points[["Season", "PointsPerMatch", "Series"]],
        ],
        ignore_index=True,
    ).sort_values("Season")

    points_chart = px.line(
        points_trend,
        x="Season",
        y="PointsPerMatch",
        color="Series",
        markers=True,
        color_discrete_map={
            selected_team: LEAGUE_COLORS.get(
                selected_league,
                "#7CB9E8",
            ),
            "League average": "#A0A6B1",
        },
        labels={
            "PointsPerMatch": "Points per match",
            "Series": "",
        },
    )

    points_chart.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Season: %{x}<br>"
            "Points per match: %{y:.2f}"
            "<extra></extra>"
        ),
    )

    points_chart.update_layout(
        height=410,
        yaxis_range=[0, 3],
        hovermode="x unified",
        legend_title_text="",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(
        points_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with trend_right:
    st.subheader("Transition metric trend")

    selected_metric_label = st.selectbox(
        "Measure",
        list(PERCENTAGE_METRICS.keys()),
    )
    selected_metric = PERCENTAGE_METRICS[selected_metric_label]

    metric_chart = px.line(
        selected_seasons,
        x="Season",
        y=selected_metric,
        markers=True,
        color_discrete_sequence=[
            LEAGUE_COLORS.get(selected_league, "#7CB9E8")
        ],
        labels={
            selected_metric: f"{selected_metric_label} (%)",
            "Season": "Season",
        },
    )

    metric_chart.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate=(
            "Season: %{x}<br>"
            f"{selected_metric_label}: %{{y:.1f}}%"
            "<extra></extra>"
        ),
    )

    metric_chart.update_layout(
        height=410,
        yaxis_range=[0, 100],
        yaxis_ticksuffix="%",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(
        metric_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

quadrant_left, quadrant_right = st.columns([1.15, 1])

with quadrant_left:
    st.subheader("Team profile within the league")

    league_teams = team_overall[
        team_overall["League"] == selected_league
    ].copy()

    lead_benchmark = safe_rate(
        league_teams,
        "ProtectedLeads",
        "LeadOpportunities",
    )
    comeback_benchmark = safe_rate(
        league_teams,
        "ComebackWins",
        "BehindOpportunities",
    )

    peers = league_teams[
        league_teams["Team"] != selected_team
    ].copy()

    quadrant_chart = go.Figure()

    quadrant_chart.add_trace(
        go.Scatter(
            x=peers["LeadShieldPct"],
            y=peers["ComebackWinRatePct"],
            mode="markers",
            name="Other teams",
            text=peers["Team"],
            customdata=peers[
                ["PointsPerMatch", "TeamProfileQuadrant"]
            ],
            marker={
                "size": 11,
                "color": "#7C8493",
                "opacity": 0.55,
            },
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Lead protection: %{x:.1f}%<br>"
                "Comeback wins: %{y:.1f}%<br>"
                "Points per match: %{customdata[0]:.2f}<br>"
                "Profile: %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

    quadrant_chart.add_trace(
        go.Scatter(
            x=[overall_row["LeadShieldPct"]],
            y=[overall_row["ComebackWinRatePct"]],
            mode="markers+text",
            name=selected_team,
            text=[selected_team],
            textposition="top center",
            marker={
                "size": 18,
                "color": LEAGUE_COLORS.get(
                    selected_league,
                    "#7CB9E8",
                ),
                "line": {"width": 2, "color": "white"},
            },
            hovertemplate=(
                f"<b>{selected_team}</b><br>"
                "Lead protection: %{x:.1f}%<br>"
                "Comeback wins: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    quadrant_chart.add_vline(
        x=lead_benchmark,
        line_dash="dash",
        line_color="#A0A6B1",
        annotation_text="League lead benchmark",
        annotation_position="top left",
    )
    quadrant_chart.add_hline(
        y=comeback_benchmark,
        line_dash="dash",
        line_color="#A0A6B1",
        annotation_text="League comeback benchmark",
        annotation_position="bottom right",
    )

    quadrant_chart.update_layout(
        height=450,
        xaxis_title="Lead protection rate (%)",
        yaxis_title="Comeback win rate (%)",
        xaxis_ticksuffix="%",
        yaxis_ticksuffix="%",
        legend_title_text="",
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(
        quadrant_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with quadrant_right:
    st.subheader("Scoring by season")

    scoring = selected_seasons[
        [
            "Season",
            "GoalsForPerMatch",
            "GoalsAgainstPerMatch",
        ]
    ].melt(
        id_vars="Season",
        var_name="Metric",
        value_name="GoalsPerMatch",
    )

    scoring["Metric"] = scoring["Metric"].replace(
        {
            "GoalsForPerMatch": "Goals scored",
            "GoalsAgainstPerMatch": "Goals conceded",
        }
    )

    scoring_chart = px.bar(
        scoring,
        x="Season",
        y="GoalsPerMatch",
        color="Metric",
        barmode="group",
        color_discrete_map={
            "Goals scored": "#7CB9E8",
            "Goals conceded": "#FF7A7A",
        },
        labels={
            "GoalsPerMatch": "Goals per match",
            "Metric": "",
        },
    )

    scoring_chart.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Season: %{x}<br>"
            "Goals per match: %{y:.2f}"
            "<extra></extra>"
        )
    )

    scoring_chart.update_layout(
        height=450,
        legend_title_text="",
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(
        scoring_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

st.subheader("Home versus away")

venue = home_away[
    (home_away["League"] == selected_league)
    & (home_away["Team"] == selected_team)
].copy()

venue_order = ["Home", "Away"]
venue["Venue"] = pd.Categorical(
    venue["Venue"],
    categories=venue_order,
    ordered=True,
)
venue = venue.sort_values("Venue")

venue_tab1, venue_tab2 = st.tabs(
    ["Results and scoring", "Match-state performance"]
)

with venue_tab1:
    venue_results = venue[
        [
            "Venue",
            "PointsPerMatch",
            "GoalsForPerMatch",
            "GoalsAgainstPerMatch",
        ]
    ].melt(
        id_vars="Venue",
        var_name="Metric",
        value_name="Value",
    )

    venue_results["Metric"] = venue_results["Metric"].replace(
        {
            "PointsPerMatch": "Points per match",
            "GoalsForPerMatch": "Goals scored",
            "GoalsAgainstPerMatch": "Goals conceded",
        }
    )

    venue_results_chart = px.bar(
        venue_results,
        x="Metric",
        y="Value",
        color="Venue",
        barmode="group",
        category_orders={"Venue": venue_order},
        color_discrete_map={
            "Home": "#7CB9E8",
            "Away": "#F4A261",
        },
        labels={"Value": "Per-match value", "Metric": ""},
    )

    venue_results_chart.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x}: %{y:.2f}"
            "<extra></extra>"
        )
    )

    venue_results_chart.update_layout(
        height=390,
        legend_title_text="Venue",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(
        venue_results_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with venue_tab2:
    venue_states = venue[
        [
            "Venue",
            "LeadShieldPct",
            "ComebackWinRatePct",
            "DrawBreakthroughRatePct",
        ]
    ].melt(
        id_vars="Venue",
        var_name="Metric",
        value_name="Rate",
    )

    venue_states["Metric"] = venue_states["Metric"].replace(
        {
            "LeadShieldPct": "Lead protection",
            "ComebackWinRatePct": "Comeback wins",
            "DrawBreakthroughRatePct": "Draw breakthroughs",
        }
    )

    venue_states_chart = px.bar(
        venue_states,
        x="Metric",
        y="Rate",
        color="Venue",
        barmode="group",
        category_orders={"Venue": venue_order},
        color_discrete_map={
            "Home": "#7CB9E8",
            "Away": "#F4A261",
        },
        labels={"Rate": "Rate (%)", "Metric": ""},
    )

    venue_states_chart.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x}: %{y:.1f}%"
            "<extra></extra>"
        )
    )

    venue_states_chart.update_layout(
        height=390,
        yaxis_ticksuffix="%",
        legend_title_text="Venue",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(
        venue_states_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

home_row = venue[venue["Venue"] == "Home"]
away_row = venue[venue["Venue"] == "Away"]

if not home_row.empty and not away_row.empty:
    home_ppm = float(home_row["PointsPerMatch"].iloc[0])
    away_ppm = float(away_row["PointsPerMatch"].iloc[0])
    home_lead = float(home_row["LeadShieldPct"].iloc[0])
    away_lead = float(away_row["LeadShieldPct"].iloc[0])

    stronger_venue = "home" if home_ppm >= away_ppm else "away"
    points_gap = abs(home_ppm - away_ppm)

    st.info(
        f"**Key observation:** {selected_team} is stronger {stronger_venue}, "
        f"with a {points_gap:.2f} points-per-match gap between venues. "
        f"Lead protection is {home_lead:.1f}% at home and {away_lead:.1f}% away."
    )