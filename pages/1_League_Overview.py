from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_csv


st.set_page_config(
    page_title="League Overview",
    page_icon="📈",
    layout="wide",
)

css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

league_season = load_csv("02_league_season_metrics.csv")
transition_matrix = load_csv("01_transition_matrix_rates.csv")

LEAGUE_COLORS = {
    "English Premier League": "#7CB9E8",
    "Spanish La Liga": "#FF5A5F",
    "Italian Serie A": "#4D96FF",
    "German Bundesliga": "#F4A261",
    "French Ligue 1": "#5CD6A0",
}

METRICS = {
    "Lead protection rate": {
        "column": "LeadShieldPct",
        "numerator": "ProtectedLeads",
        "denominator": "LeadOpportunities",
        "description": "Share of halftime leads that were still wins at full time.",
    },
    "Comeback win rate": {
        "column": "ComebackWinRatePct",
        "numerator": "ComebackWins",
        "denominator": "BehindOpportunities",
        "description": "Share of halftime deficits converted into full-time wins.",
    },
    "Draw breakthrough rate": {
        "column": "DrawBreakthroughRatePct",
        "numerator": "DrawBreakthroughs",
        "denominator": "LevelOpportunities",
        "description": "Share of halftime draws converted into full-time wins.",
    },
    "State-change rate": {
        "column": "StateChangeRatePct",
        "numerator": "StateChanges",
        "denominator": "TeamMatchRows",
        "description": "Share of team-match states that changed after halftime.",
    },
    "Match volatility rate": {
        "column": "MatchVolatilityRatePct",
        "numerator": "VolatileMatches",
        "denominator": "MatchRows",
        "description": "Share of matches classified as volatile.",
    },
    "Average total goals": {
        "column": "AvgTotalGoals",
        "numerator": "GoalsFor",
        "denominator": "MatchRows",
        "description": "Average combined goals scored per match.",
    },
}


def safe_rate(frame: pd.DataFrame, numerator: str, denominator: str) -> float:
    denominator_sum = frame[denominator].sum()
    if denominator_sum == 0:
        return 0.0
    return float(frame[numerator].sum() / denominator_sum * 100)


def weighted_average(
    frame: pd.DataFrame,
    value_column: str,
    weight_column: str,
) -> float:
    valid = frame[[value_column, weight_column]].dropna()
    weight_sum = valid[weight_column].sum()
    if valid.empty or weight_sum == 0:
        return 0.0
    return float(
        (valid[value_column] * valid[weight_column]).sum() / weight_sum
    )


def aggregate_metric(
    frame: pd.DataFrame,
    metric_name: str,
) -> float:
    config = METRICS[metric_name]
    if metric_name == "Average total goals":
        return weighted_average(frame, config["column"], "MatchRows")
    return safe_rate(
        frame,
        config["numerator"],
        config["denominator"],
    )


st.title("📈 League Transition Overview")
st.caption(
    "Compare how matches evolve from halftime to full time across "
    "Europe’s five major football leagues."
)

all_leagues = sorted(league_season["League"].dropna().unique())
all_seasons = sorted(league_season["Season"].dropna().astype(str).unique())

with st.sidebar:
    st.header("Filters")

    league_choice = st.selectbox(
        "League",
        ["All leagues"] + all_leagues,
    )

    start_season, end_season = st.select_slider(
        "Season range",
        options=all_seasons,
        value=(all_seasons[0], all_seasons[-1]),
    )

    st.divider()
    st.caption(
        "All charts and indicators update together according to these filters."
    )

start_index = all_seasons.index(start_season)
end_index = all_seasons.index(end_season)
selected_seasons = all_seasons[start_index : end_index + 1]

filtered = league_season[
    league_season["Season"].astype(str).isin(selected_seasons)
].copy()

if league_choice != "All leagues":
    filtered = filtered[filtered["League"] == league_choice].copy()

matrix_filtered = transition_matrix[
    transition_matrix["Season"].astype(str).isin(selected_seasons)
].copy()

if league_choice != "All leagues":
    matrix_filtered = matrix_filtered[
        matrix_filtered["League"] == league_choice
    ].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

total_matches = int(filtered["MatchRows"].sum())
average_goals = weighted_average(filtered, "AvgTotalGoals", "MatchRows")
lead_protection = safe_rate(
    filtered,
    "ProtectedLeads",
    "LeadOpportunities",
)
comeback_rate = safe_rate(
    filtered,
    "ComebackWins",
    "BehindOpportunities",
)
volatility_rate = safe_rate(
    filtered,
    "VolatileMatches",
    "MatchRows",
)

scope_label = (
    "All five leagues"
    if league_choice == "All leagues"
    else league_choice
)

st.markdown(
    f"""
    <div class="section-note">
        <strong>Current view:</strong> {scope_label},
        seasons {start_season}–{end_season}.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Performance snapshot")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Matches", f"{total_matches:,}")
kpi2.metric("Goals per match", f"{average_goals:.2f}")
kpi3.metric("Lead protection", f"{lead_protection:.1f}%")
kpi4.metric("Comeback wins", f"{comeback_rate:.1f}%")
kpi5.metric("Volatile matches", f"{volatility_rate:.1f}%")

st.subheader("Seasonal development")

metric_name = st.selectbox(
    "Choose the measure shown over time",
    list(METRICS.keys()),
)
metric_config = METRICS[metric_name]

st.caption(metric_config["description"])

trend_rows = []
for (league, season), group in filtered.groupby(["League", "Season"]):
    trend_rows.append(
        {
            "League": league,
            "Season": str(season),
            "Value": aggregate_metric(group, metric_name),
        }
    )

trend = pd.DataFrame(trend_rows)
trend["Season"] = pd.Categorical(
    trend["Season"],
    categories=selected_seasons,
    ordered=True,
)
trend = trend.sort_values(["Season", "League"])

value_suffix = "" if metric_name == "Average total goals" else "%"

trend_chart = px.line(
    trend,
    x="Season",
    y="Value",
    color="League",
    markers=True,
    color_discrete_map=LEAGUE_COLORS,
    labels={
        "Season": "Season",
        "Value": metric_name,
        "League": "League",
    },
)

trend_chart.update_traces(
    line=dict(width=3),
    marker=dict(size=8),
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Season: %{x}<br>"
        f"{metric_name}: %{{y:.2f}}{value_suffix}"
        "<extra></extra>"
    ),
)

trend_chart.update_layout(
    height=430,
    hovermode="x unified",
    legend_title_text="League",
    margin=dict(l=20, r=20, t=25, b=20),
    yaxis_ticksuffix=value_suffix,
)

st.plotly_chart(
    trend_chart,
    use_container_width=True,
    config={"displayModeBar": False},
)

left_column, right_column = st.columns([1.15, 1])

with left_column:
    st.subheader("League comparison")

    comparison_rows = []
    comparison_metrics = [
        "Lead protection rate",
        "Comeback win rate",
        "Match volatility rate",
    ]

    for league, group in filtered.groupby("League"):
        for comparison_metric in comparison_metrics:
            comparison_rows.append(
                {
                    "League": league,
                    "Metric": comparison_metric.replace(" rate", ""),
                    "Rate": aggregate_metric(group, comparison_metric),
                }
            )

    comparison = pd.DataFrame(comparison_rows)

    comparison_chart = px.bar(
        comparison,
        x="League",
        y="Rate",
        color="Metric",
        barmode="group",
        labels={
            "League": "League",
            "Rate": "Rate (%)",
            "Metric": "Measure",
        },
    )

    comparison_chart.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{fullData.name}: %{y:.1f}%"
            "<extra></extra>"
        )
    )

    comparison_chart.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=25, b=20),
        legend_title_text="Measure",
        yaxis_ticksuffix="%",
    )

    st.plotly_chart(
        comparison_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with right_column:
    st.subheader("Halftime → full-time outcomes")

    matrix_summary = (
        matrix_filtered.groupby(
            ["HalfTimeState", "FullTimeState"],
            as_index=False,
        )
        .agg(
            TeamMatchRows=("TeamMatchRows", "sum"),
            HalfTimeStateTotal=("HalfTimeStateTotal", "sum"),
        )
    )

    matrix_summary["TransitionRatePct"] = (
        matrix_summary["TeamMatchRows"]
        / matrix_summary["HalfTimeStateTotal"]
        * 100
    )

    state_order = ["Ahead", "Level", "Behind"]

    matrix_pivot = (
        matrix_summary.pivot(
            index="HalfTimeState",
            columns="FullTimeState",
            values="TransitionRatePct",
        )
        .reindex(index=state_order, columns=["Win", "Draw", "Loss"])
        .fillna(0)
    )

    matrix_pivot.index = ["Ahead", "Draw", "Behind"]

    matrix_chart = go.Figure(
        data=go.Heatmap(
            z=matrix_pivot.values,
            x=matrix_pivot.columns,
            y=matrix_pivot.index,
            text=[
                [f"{value:.1f}%" for value in row]
                for row in matrix_pivot.values
            ],
            texttemplate="%{text}",
            textfont={"size": 15},
            colorscale=[
                [0.0, "#172033"],
                [0.5, "#2D5F8B"],
                [1.0, "#78C6FF"],
            ],
            colorbar={
                "title": "Rate",
                "ticksuffix": "%",
            },
            hovertemplate=(
                "Halftime: %{y}<br>"
                "Full time: %{x}<br>"
                "Rate: %{z:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    matrix_chart.update_layout(
        height=430,
        xaxis_title="Full-time state",
        yaxis_title="Halftime state",
        margin=dict(l=20, r=20, t=25, b=20),
    )

    st.plotly_chart(
        matrix_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )

st.subheader("What stands out?")

league_summary_rows = []
for league, group in filtered.groupby("League"):
    league_summary_rows.append(
        {
            "League": league,
            "LeadProtection": safe_rate(
                group,
                "ProtectedLeads",
                "LeadOpportunities",
            ),
            "ComebackRate": safe_rate(
                group,
                "ComebackWins",
                "BehindOpportunities",
            ),
            "Volatility": safe_rate(
                group,
                "VolatileMatches",
                "MatchRows",
            ),
        }
    )

league_summary = pd.DataFrame(league_summary_rows)

if len(league_summary) > 1:
    strongest_protection = league_summary.loc[
        league_summary["LeadProtection"].idxmax()
    ]
    highest_volatility = league_summary.loc[
        league_summary["Volatility"].idxmax()
    ]
    highest_comeback = league_summary.loc[
        league_summary["ComebackRate"].idxmax()
    ]

    insight1, insight2, insight3 = st.columns(3)

    with insight1:
        st.info(
            f"**Best lead protection:** "
            f"{strongest_protection['League']} "
            f"({strongest_protection['LeadProtection']:.1f}%)."
        )

    with insight2:
        st.info(
            f"**Highest comeback rate:** "
            f"{highest_comeback['League']} "
            f"({highest_comeback['ComebackRate']:.1f}%)."
        )

    with insight3:
        st.info(
            f"**Most volatile:** "
            f"{highest_volatility['League']} "
            f"({highest_volatility['Volatility']:.1f}%)."
        )
else:
    best_season = trend.loc[trend["Value"].idxmax()]
    worst_season = trend.loc[trend["Value"].idxmin()]

    st.info(
        f"For **{league_choice}**, the highest value of "
        f"**{metric_name.lower()}** occurred in "
        f"**{best_season['Season']}** ({best_season['Value']:.2f}{value_suffix}), "
        f"while the lowest occurred in "
        f"**{worst_season['Season']}** ({worst_season['Value']:.2f}{value_suffix})."
    )