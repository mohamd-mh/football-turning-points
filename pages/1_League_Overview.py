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

# Page-specific visual refinements.
st.markdown(
    """
    <style>
    .interaction-note {
        padding: 0.72rem 0.9rem;
        border: 1px solid rgba(124, 185, 232, 0.28);
        border-radius: 10px;
        background: rgba(124, 185, 232, 0.055);
        margin-top: 0.35rem;
        margin-bottom: 0.85rem;
        font-size: 0.9rem;
        opacity: 0.92;
    }

    .insight-card {
        min-height: 108px;
        padding: 0.9rem 1rem;
        border: 1px solid rgba(128, 128, 128, 0.24);
        border-radius: 12px;
        background: rgba(128, 128, 128, 0.035);
    }

    .insight-label {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.04rem;
        opacity: 0.62;
        margin-bottom: 0.32rem;
        text-transform: uppercase;
    }

    .insight-value {
        font-size: 1rem;
        font-weight: 700;
        line-height: 1.38;
    }

    .insight-detail {
        font-size: 0.82rem;
        opacity: 0.72;
        margin-top: 0.25rem;
    }
    </style>
    """,
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

LEAGUE_SHORT = {
    "English Premier League": "Premier League",
    "Spanish La Liga": "La Liga",
    "Italian Serie A": "Serie A",
    "German Bundesliga": "Bundesliga",
    "French Ligue 1": "Ligue 1",
}

METRICS = {
    "Lead protection rate": {
        "column": "LeadShieldPct",
        "numerator": "ProtectedLeads",
        "denominator": "LeadOpportunities",
        "description": (
            "Percentage of halftime leads that were still wins at full time."
        ),
        "suffix": "%",
        "decimals": 1,
    },
    "Comeback win rate": {
        "column": "ComebackWinRatePct",
        "numerator": "ComebackWins",
        "denominator": "BehindOpportunities",
        "description": (
            "Percentage of halftime deficits converted into full-time wins."
        ),
        "suffix": "%",
        "decimals": 1,
    },
    "Draw breakthrough rate": {
        "column": "DrawBreakthroughRatePct",
        "numerator": "DrawBreakthroughs",
        "denominator": "LevelOpportunities",
        "description": (
            "Percentage of halftime draws converted into full-time wins."
        ),
        "suffix": "%",
        "decimals": 1,
    },
    "State-change rate": {
        "column": "StateChangeRatePct",
        "numerator": "StateChanges",
        "denominator": "TeamMatchRows",
        "description": (
            "Percentage of team-match states that changed after halftime."
        ),
        "suffix": "%",
        "decimals": 1,
    },
    "Match volatility rate": {
        "column": "MatchVolatilityRatePct",
        "numerator": "VolatileMatches",
        "denominator": "MatchRows",
        "description": (
            "Percentage of matches classified as volatile."
        ),
        "suffix": "%",
        "decimals": 1,
    },
    "Average total goals": {
        "column": "AvgTotalGoals",
        "numerator": None,
        "denominator": "MatchRows",
        "description": "Average combined goals scored per match.",
        "suffix": "",
        "decimals": 2,
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


def aggregate_metric(frame: pd.DataFrame, metric_name: str) -> float:
    config = METRICS[metric_name]

    if metric_name == "Average total goals":
        return weighted_average(
            frame,
            config["column"],
            "MatchRows",
        )

    return safe_rate(
        frame,
        config["numerator"],
        config["denominator"],
    )


def format_metric(value: float, metric_name: str) -> str:
    config = METRICS[metric_name]
    decimals = config["decimals"]
    suffix = config["suffix"]
    return f"{value:.{decimals}f}{suffix}"


def spread_label_positions(
    values: dict[str, float],
    minimum_gap: float,
) -> dict[str, float]:
    """
    Spread labels vertically while preserving their order.
    This prevents direct line labels from covering each other.
    """
    if len(values) <= 1:
        return values.copy()

    ordered = sorted(values.items(), key=lambda item: item[1])
    adjusted = {ordered[0][0]: ordered[0][1]}
    previous = ordered[0][1]

    for league, value in ordered[1:]:
        new_value = max(value, previous + minimum_gap)
        adjusted[league] = new_value
        previous = new_value

    return adjusted


# ---------------------------------------------------------------------
# Session state for coordinated / linked chart selection
# ---------------------------------------------------------------------
if "league_linked_selection" not in st.session_state:
    st.session_state.league_linked_selection = None

if "league_chart_epoch" not in st.session_state:
    st.session_state.league_chart_epoch = 0


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
st.title("📈 League Transition Overview")
st.caption(
    "Compare how matches evolve from halftime to full time across "
    "Europe’s five major football leagues."
)


# ---------------------------------------------------------------------
# Global controls
# ---------------------------------------------------------------------
all_leagues = sorted(league_season["League"].dropna().unique())
all_seasons = sorted(league_season["Season"].dropna().astype(str).unique())

with st.sidebar:
    st.header("Filters")

    league_choice = st.selectbox(
        "League",
        ["All leagues"] + all_leagues,
        key="league_overview_sidebar_league",
    )

    start_season, end_season = st.select_slider(
        "Seasons",
        options=all_seasons,
        value=(all_seasons[0], all_seasons[-1]),
        key="league_overview_seasons",
    )

    # Explicit sidebar selection takes precedence over linked chart selection.
    if league_choice != "All leagues":
        if st.session_state.league_linked_selection is not None:
            st.session_state.league_linked_selection = None
            st.session_state.league_chart_epoch += 1

    if (
        league_choice == "All leagues"
        and st.session_state.league_linked_selection is not None
    ):
        st.divider()
        st.caption("Linked chart selection")
        st.markdown(
            f"**{st.session_state.league_linked_selection}**"
        )

        if st.button(
            "Reset linked selection",
            width="stretch",
            key="reset_league_link",
        ):
            st.session_state.league_linked_selection = None
            st.session_state.league_chart_epoch += 1
            st.rerun()

    st.divider()
    st.caption(
        "The league filter, season range, chart selection, KPIs, "
        "ranking, and transition matrix are coordinated."
    )


start_index = all_seasons.index(start_season)
end_index = all_seasons.index(end_season)
selected_seasons = all_seasons[start_index : end_index + 1]

season_base = league_season[
    league_season["Season"].astype(str).isin(selected_seasons)
].copy()

matrix_season_base = transition_matrix[
    transition_matrix["Season"].astype(str).isin(selected_seasons)
].copy()

linked_league = (
    st.session_state.league_linked_selection
    if league_choice == "All leagues"
    else None
)

effective_league = (
    league_choice
    if league_choice != "All leagues"
    else linked_league
)

if effective_league is None:
    focused = season_base.copy()
    matrix_focused = matrix_season_base.copy()
else:
    focused = season_base[
        season_base["League"] == effective_league
    ].copy()
    matrix_focused = matrix_season_base[
        matrix_season_base["League"] == effective_league
    ].copy()

if focused.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


# ---------------------------------------------------------------------
# Current-view indicator
# ---------------------------------------------------------------------
if effective_league is None:
    scope_label = "All five leagues"
else:
    scope_label = effective_league

link_note = ""
if linked_league is not None:
    link_note = " — selected directly from the trend chart"

st.markdown(
    f"""
    <div class="section-note">
        <strong>Current view:</strong> {scope_label}{link_note},
        seasons {start_season}–{end_season}.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# KPI overview
# ---------------------------------------------------------------------
st.subheader("Performance snapshot")

total_matches = int(focused["MatchRows"].sum())
average_goals = weighted_average(
    focused,
    "AvgTotalGoals",
    "MatchRows",
)
lead_protection = safe_rate(
    focused,
    "ProtectedLeads",
    "LeadOpportunities",
)
comeback_rate = safe_rate(
    focused,
    "ComebackWins",
    "BehindOpportunities",
)
volatility_rate = safe_rate(
    focused,
    "VolatileMatches",
    "MatchRows",
)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Matches", f"{total_matches:,}")
kpi2.metric("Goals per match", f"{average_goals:.2f}")
kpi3.metric("Lead protection rate", f"{lead_protection:.1f}%")
kpi4.metric("Comeback win rate", f"{comeback_rate:.1f}%")
kpi5.metric("Match volatility rate", f"{volatility_rate:.1f}%")


# ---------------------------------------------------------------------
# Temporal overview + linked selection
# ---------------------------------------------------------------------
st.subheader("How has match behavior changed over time?")

metric_name = st.selectbox(
    "Measure",
    list(METRICS.keys()),
    key="league_overview_metric",
)
metric_config = METRICS[metric_name]

st.caption(metric_config["description"])

# The trend intentionally keeps all leagues visible when the sidebar is on
# "All leagues", even after a linked selection, so the user retains context.
if league_choice == "All leagues":
    trend_source = season_base.copy()
else:
    trend_source = focused.copy()

trend_rows = []
for (league, season), group in trend_source.groupby(["League", "Season"]):
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

trend_chart = px.line(
    trend,
    x="Season",
    y="Value",
    color="League",
    markers=True,
    color_discrete_map=LEAGUE_COLORS,
    custom_data=["League"],
    labels={
        "Season": "Season",
        "Value": metric_name,
        "League": "League",
    },
)

for trace in trend_chart.data:
    is_linked = (
        linked_league is not None
        and trace.name == linked_league
    )

    if linked_league is None:
        trace.update(
            line=dict(width=3),
            marker=dict(size=8),
            opacity=1.0,
        )
    elif is_linked:
        trace.update(
            line=dict(width=4.5),
            marker=dict(size=10),
            opacity=1.0,
        )
    else:
        trace.update(
            line=dict(width=2),
            marker=dict(size=6),
            opacity=0.24,
        )

    trace.hovertemplate = (
        "<b>%{fullData.name}</b><br>"
        "Season: %{x}<br>"
        f"{metric_name}: %{{y:.{metric_config['decimals']}f}}"
        f"{metric_config['suffix']}"
        "<extra></extra>"
    )

# Direct end labels remove the need to repeatedly scan between lines and legend.
if len(trend["League"].unique()) > 1:
    final_season = selected_seasons[-1]
    final_points = trend[
        trend["Season"].astype(str) == final_season
    ].copy()

    final_values = {
        row["League"]: float(row["Value"])
        for _, row in final_points.iterrows()
    }

    if metric_config["suffix"] == "%":
        minimum_gap = 1.45
    else:
        minimum_gap = 0.10

    label_positions = spread_label_positions(
        final_values,
        minimum_gap,
    )

    for league, actual_y in final_values.items():
        label_y = label_positions[league]
        is_muted = (
            linked_league is not None
            and league != linked_league
        )

        annotation_color = (
            "#8A909B"
            if is_muted
            else LEAGUE_COLORS.get(league, "#FFFFFF")
        )

        # A light connector helps if the label was shifted to avoid overlap.
        if abs(label_y - actual_y) > 1e-9:
            trend_chart.add_shape(
                type="line",
                x0=final_season,
                x1=final_season,
                y0=actual_y,
                y1=label_y,
                line=dict(
                    color=annotation_color,
                    width=1,
                    dash="dot",
                ),
            )

        trend_chart.add_annotation(
            x=final_season,
            y=label_y,
            text=LEAGUE_SHORT.get(league, league),
            showarrow=False,
            xshift=16,
            xanchor="left",
            font=dict(
                size=12,
                color=annotation_color,
            ),
            opacity=0.5 if is_muted else 1.0,
        )

trend_chart.update_layout(
    height=455,
    hovermode="closest",
    showlegend=False,
    margin=dict(
        l=20,
        r=160 if len(trend["League"].unique()) > 1 else 20,
        t=20,
        b=20,
    ),
)

if metric_config["suffix"] == "%":
    trend_chart.update_yaxes(ticksuffix="%")

trend_event = st.plotly_chart(
    trend_chart,
    width="stretch",
    config={
        "displayModeBar": False,
        "scrollZoom": False,
    },
    key=f"league_trend_select_{st.session_state.league_chart_epoch}",
    on_select="rerun" if league_choice == "All leagues" else "ignore",
    selection_mode="points",
)

if league_choice == "All leagues":
    st.markdown(
        """
        <div class="interaction-note">
            <strong>Interactive link:</strong> click any point on a league line
            to focus the KPI cards, ranking chart, transition matrix, and
            interpretation on that league. The other lines remain visible as context.
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_points = []
    try:
        selected_points = trend_event.selection.points
    except (AttributeError, TypeError):
        selected_points = []

    if selected_points:
        point = selected_points[0]

        selected_from_chart = None

        # customdata is the most explicit source.
        customdata = point.get("customdata")
        if customdata:
            selected_from_chart = customdata[0]

        # Fallback for Plotly selection objects that expose legendgroup.
        if selected_from_chart is None:
            selected_from_chart = point.get("legendgroup")

        if (
            selected_from_chart in all_leagues
            and selected_from_chart
            != st.session_state.league_linked_selection
        ):
            st.session_state.league_linked_selection = selected_from_chart
            st.rerun()


# ---------------------------------------------------------------------
# Comparison + transition matrix
# ---------------------------------------------------------------------
comparison_col, matrix_col = st.columns([1.02, 1])

with comparison_col:
    st.subheader("Which league leads on this measure?")
    st.caption(
        f"Ranked comparison of {metric_name.lower()} across leagues for the selected seasons."
    )

    ranking_rows = []
    for league, group in season_base.groupby("League"):
        ranking_rows.append(
            {
                "League": league,
                "Value": aggregate_metric(group, metric_name),
            }
        )

    ranking = (
        pd.DataFrame(ranking_rows)
        .sort_values("Value", ascending=True)
        .reset_index(drop=True)
    )

    focus_for_highlight = effective_league

    # Ranked dot plot: position on a shared scale makes close league
    # values easier to compare than nearly identical bar lengths.
    short_names = [
        LEAGUE_SHORT.get(league, league)
        for league in ranking["League"]
    ]

    marker_colors = []
    marker_sizes = []
    for league in ranking["League"]:
        if focus_for_highlight is None:
            marker_colors.append("#7CB9E8")
            marker_sizes.append(15)
        elif league == focus_for_highlight:
            marker_colors.append("#7CB9E8")
            marker_sizes.append(19)
        else:
            marker_colors.append("#66707E")
            marker_sizes.append(12)

    values = ranking["Value"].astype(float)
    value_min = float(values.min())
    value_max = float(values.max())

    if metric_config["suffix"] == "%":
        # Preserve meaningful percentage context rather than tightly zooming
        # around tiny differences.
        x_low = max(0.0, value_min - 5.0)
        x_high = min(100.0, value_max + 5.0)
    else:
        spread = max(value_max - value_min, 0.1)
        pad = max(spread * 0.8, 0.20)
        x_low = max(0.0, value_min - pad)
        x_high = value_max + pad

    ranking_chart = go.Figure()

    for y_name, value in zip(short_names, values):
        ranking_chart.add_shape(
            type="line",
            x0=x_low,
            x1=float(value),
            y0=y_name,
            y1=y_name,
            line=dict(
                color="rgba(150,160,175,0.20)",
                width=1,
            ),
            layer="below",
        )

    ranking_chart.add_trace(
        go.Scatter(
            x=values,
            y=short_names,
            mode="markers+text",
            marker=dict(
                size=marker_sizes,
                color=marker_colors,
                line=dict(
                    color="rgba(255,255,255,0.80)",
                    width=1,
                ),
            ),
            text=[
                format_metric(value, metric_name)
                for value in values
            ],
            textposition="middle right",
            textfont=dict(size=12),
            customdata=ranking[["League"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{metric_name}: "
                f"%{{x:.{metric_config['decimals']}f}}"
                f"{metric_config['suffix']}"
                "<extra></extra>"
            ),
            cliponaxis=False,
            showlegend=False,
        )
    )

    ranking_chart.update_layout(
        height=430,
        showlegend=False,
        margin=dict(l=20, r=80, t=15, b=20),
        xaxis_title=metric_name,
        yaxis_title="",
        xaxis=dict(
            range=[x_low, x_high],
            showgrid=True,
            zeroline=False,
        ),
    )

    if metric_config["suffix"] == "%":
        ranking_chart.update_xaxes(ticksuffix="%")

    st.plotly_chart(
        ranking_chart,
        width="stretch",
        config={"displayModeBar": False},
    )

with matrix_col:
    st.subheader("What happens after halftime?")
    st.caption(
        "Rows show the team's state at halftime; columns show its "
        "state at full time."
    )

    matrix_work = matrix_focused.copy()

    # The processed CSV uses "Level"; display it as the clearer user-facing
    # term "Draw".
    matrix_work["HalfTimeStateDisplay"] = (
        matrix_work["HalfTimeState"]
        .replace({"Level": "Draw"})
    )

    matrix_summary = (
        matrix_work.groupby(
            ["HalfTimeStateDisplay", "FullTimeState"],
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

    state_order = ["Ahead", "Draw", "Behind"]
    result_order = ["Win", "Draw", "Loss"]

    matrix_pivot = (
        matrix_summary.pivot(
            index="HalfTimeStateDisplay",
            columns="FullTimeState",
            values="TransitionRatePct",
        )
        .reindex(
            index=state_order,
            columns=result_order,
        )
        .fillna(0)
    )

    matrix_chart = go.Figure(
        data=go.Heatmap(
            z=matrix_pivot.values,
            x=matrix_pivot.columns,
            y=matrix_pivot.index,
            colorscale=[
                [0.0, "#172033"],
                [0.5, "#2D5F8B"],
                [1.0, "#78C6FF"],
            ],
            zmin=0,
            zmax=100,
            colorbar={
                "title": "Rate",
                "ticksuffix": "%",
                "thickness": 12,
            },
            hovertemplate=(
                "Halftime: %{y}<br>"
                "Full time: %{x}<br>"
                "Rate: %{z:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    # Per-cell text contrast keeps percentages legible on both dark
    # and bright sequential-color cells.
    for y_state in matrix_pivot.index:
        for x_state in matrix_pivot.columns:
            value = float(matrix_pivot.loc[y_state, x_state])
            text_color = "#0C1824" if value >= 58 else "#FFFFFF"

            matrix_chart.add_annotation(
                x=x_state,
                y=y_state,
                text=f"{value:.1f}%",
                showarrow=False,
                font=dict(
                    size=15,
                    color=text_color,
                ),
            )

    matrix_chart.update_layout(
        height=430,
        xaxis_title="Full-time state",
        yaxis_title="Halftime state",
        margin=dict(l=20, r=20, t=15, b=20),
    )

    st.plotly_chart(
        matrix_chart,
        width="stretch",
        config={"displayModeBar": False},
    )


# ---------------------------------------------------------------------
# Interpretation / findings
# ---------------------------------------------------------------------
st.subheader("What stands out?")

if effective_league is None:
    league_summary_rows = []

    for league, group in season_base.groupby("League"):
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

    strongest_protection = league_summary.loc[
        league_summary["LeadProtection"].idxmax()
    ]
    highest_comeback = league_summary.loc[
        league_summary["ComebackRate"].idxmax()
    ]
    highest_volatility = league_summary.loc[
        league_summary["Volatility"].idxmax()
    ]

    insight1, insight2, insight3 = st.columns(3)

    with insight1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Best lead protection</div>
                <div class="insight-value">
                    {strongest_protection['League']}
                </div>
                <div class="insight-detail">
                    {strongest_protection['LeadProtection']:.1f}% of halftime leads
                    were protected.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight2:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Highest comeback win rate</div>
                <div class="insight-value">
                    {highest_comeback['League']}
                </div>
                <div class="insight-detail">
                    {highest_comeback['ComebackRate']:.1f}% of halftime deficits
                    became wins.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight3:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Highest volatility</div>
                <div class="insight-value">
                    {highest_volatility['League']}
                </div>
                <div class="insight-detail">
                    {highest_volatility['Volatility']:.1f}% of matches were
                    classified as volatile.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    focused_trend_rows = []

    for season, group in focused.groupby("Season"):
        focused_trend_rows.append(
            {
                "Season": str(season),
                "Value": aggregate_metric(group, metric_name),
            }
        )

    focused_trend = pd.DataFrame(focused_trend_rows)

    if not focused_trend.empty:
        best_season = focused_trend.loc[
            focused_trend["Value"].idxmax()
        ]
        lowest_season = focused_trend.loc[
            focused_trend["Value"].idxmin()
        ]

        focused_lead = safe_rate(
            focused,
            "ProtectedLeads",
            "LeadOpportunities",
        )
        focused_comeback = safe_rate(
            focused,
            "ComebackWins",
            "BehindOpportunities",
        )

        insight1, insight2, insight3 = st.columns(3)

        with insight1:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-label">Peak selected measure</div>
                    <div class="insight-value">
                        {best_season['Season']}
                    </div>
                    <div class="insight-detail">
                        {metric_name}: {format_metric(best_season['Value'], metric_name)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with insight2:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-label">Lead protection</div>
                    <div class="insight-value">
                        {focused_lead:.1f}%
                    </div>
                    <div class="insight-detail">
                        Across the selected seasons for {effective_league}.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with insight3:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-label">Comeback win rate</div>
                    <div class="insight-value">
                        {focused_comeback:.1f}%
                    </div>
                    <div class="insight-detail">
                        Across the selected seasons for {effective_league}.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )