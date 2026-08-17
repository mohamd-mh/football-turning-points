from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_csv


# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Match Cases",
    page_icon="🔎",
    layout="wide",
)

css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    .case-insight-card {
        padding: 0.95rem 1.05rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
        background: rgba(128, 128, 128, 0.035);
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .case-insight-label {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.04rem;
        text-transform: uppercase;
        opacity: 0.62;
        margin-bottom: 0.3rem;
    }

    .case-insight-text {
        font-size: 0.98rem;
        font-weight: 650;
        line-height: 1.5;
    }

    .case-guidance {
        margin-top: -0.2rem;
        margin-bottom: 0.75rem;
        opacity: 0.72;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------
transition_cases = load_csv("08_team_transition_cases.csv")
outlier_cases = load_csv("09_match_outlier_cases.csv")


# ---------------------------------------------------------------------
# Semantic constants
# ---------------------------------------------------------------------
CASE_ORDER = [
    "Comeback Win",
    "Recovery Draw",
    "Draw Breakthrough",
    "Lead Collapse",
]

CASE_COLORS = {
    "Comeback Win": "#5CD6A0",
    "Recovery Draw": "#7CB9E8",
    "Draw Breakthrough": "#F4A261",
    "Lead Collapse": "#FF6B6B",
}

# These names intentionally match the CaseType values in
# data/09_match_outlier_cases.csv exactly.
OUTLIER_ORDER = [
    "Highest Swing Intensity",
    "Highest-Scoring Matches",
    "Most Cards",
    "Most Shots with Few Goals",
]

OUTLIER_LABELS = {
    "Highest Swing Intensity": "Swing intensity",
    "Highest-Scoring Matches": "Total goals",
    "Most Cards": "Total cards",
    # CaseRankMetric is a prepared ranking value for this composite category.
    # We avoid claiming a formula that is not encoded in this visualization file.
    "Most Shots with Few Goals": "Shots-with-few-goals rank value",
}

OUTLIER_INSIGHT_LABELS = {
    "Highest Swing Intensity": "Top swing-intensity outlier",
    "Highest-Scoring Matches": "Highest-scoring match",
    "Most Cards": "Most-card match",
    "Most Shots with Few Goals": "Top shots-with-few-goals case",
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def physical_matches(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Return one row per physical match.

    The turning-point file is team-perspective based, so the same MatchID can
    legitimately appear more than once (for example, one comeback and one
    collapse). Match-level statistics and densities must therefore deduplicate
    MatchID first.
    """
    return frame.drop_duplicates(subset=["MatchID"]).copy()


def format_match_label(row: pd.Series) -> str:
    return (
        f"{row['HomeTeam']} {row['FullTimeScore']} "
        f"{row['AwayTeam']}"
    )


def make_density_heatmap(
    frame: pd.DataFrame,
    x_column: str,
    y_column: str,
    x_title: str,
    y_title: str,
    height: int = 430,
) -> go.Figure:
    if frame.empty:
        return go.Figure()

    x_min = float(frame[x_column].min())
    x_max = float(frame[x_column].max())
    y_min = float(frame[y_column].min())
    y_max = float(frame[y_column].max())

    # Shots span a wider integer range, so two-shot bins reduce noise.
    # Goals are much sparser and remain in one-goal bins.
    x_start = max(0.0, x_min - 1.0)
    x_end = x_max + 2.0
    y_start = max(-0.5, y_min - 0.5)
    y_end = y_max + 0.5

    fig = go.Figure(
        go.Histogram2d(
            x=frame[x_column],
            y=frame[y_column],
            xbins=dict(
                start=x_start,
                end=x_end,
                size=2,
            ),
            ybins=dict(
                start=y_start,
                end=y_end,
                size=1,
            ),
            colorscale=[
                [0.0, "#172033"],
                [0.35, "#244B70"],
                [0.70, "#4C91C8"],
                [1.0, "#9BD6FF"],
            ],
            colorbar=dict(
                title="Matches",
                thickness=12,
            ),
            hovertemplate=(
                f"{x_title}: %{{x}}<br>"
                f"{y_title}: %{{y}}<br>"
                "Unique matches in bin: %{z}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=25, t=15, b=20),
        xaxis_title=x_title,
        yaxis_title=y_title,
    )

    return fig


def quiet_insight(label: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="case-insight-card">
            <div class="case-insight-label">{label}</div>
            <div class="case-insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_number(value: float, decimals: int = 1) -> str:
    return f"{float(value):.{decimals}f}"


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
st.title("🔎 Match Cases and Outliers")
st.caption(
    "Move from aggregate patterns to the individual matches behind "
    "comebacks, collapses, recoveries, breakthroughs, and statistical extremes."
)


# ---------------------------------------------------------------------
# Shared global filters
# ---------------------------------------------------------------------
all_leagues = sorted(transition_cases["League"].dropna().unique())
all_seasons = sorted(
    transition_cases["Season"].dropna().astype(str).unique()
)

with st.sidebar:
    st.header("Global filters")

    selected_league = st.selectbox(
        "League",
        ["All leagues"] + all_leagues,
        key="match_cases_league",
    )

    start_season, end_season = st.select_slider(
        "Seasons",
        options=all_seasons,
        value=(all_seasons[0], all_seasons[-1]),
        key="match_cases_seasons",
    )

    st.divider()
    st.caption(
        "Both analytical tabs use the same league and season scope."
    )

start_index = all_seasons.index(start_season)
end_index = all_seasons.index(end_season)
selected_seasons = all_seasons[start_index : end_index + 1]

transition_filtered = transition_cases[
    transition_cases["Season"].astype(str).isin(selected_seasons)
].copy()

outlier_filtered = outlier_cases[
    outlier_cases["Season"].astype(str).isin(selected_seasons)
].copy()

if selected_league != "All leagues":
    transition_filtered = transition_filtered[
        transition_filtered["League"] == selected_league
    ].copy()

    outlier_filtered = outlier_filtered[
        outlier_filtered["League"] == selected_league
    ].copy()

scope_text = (
    "All five leagues"
    if selected_league == "All leagues"
    else selected_league
)

st.markdown(
    f"""
    <div class="section-note">
        <strong>Current view:</strong> {scope_text},
        seasons {start_season}–{end_season}.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Main analytical tabs
# ---------------------------------------------------------------------
turning_tab, outlier_tab = st.tabs(
    ["Turning-point cases", "Outlier explorer"]
)


# =====================================================================
# TAB 1 — Turning-point cases
# =====================================================================
with turning_tab:
    st.subheader("Halftime turning-point cases")
    st.markdown(
        """
        <div class="case-guidance">
            The source file is team-perspective based: one physical match can
            generate more than one case record. Match-level KPIs and densities
            below therefore use one row per unique MatchID.
        </div>
        """,
        unsafe_allow_html=True,
    )

    available_case_types = [
        case_type
        for case_type in CASE_ORDER
        if case_type in set(
            transition_filtered["CaseType"].dropna().unique()
        )
    ]

    selected_case = st.selectbox(
        "Case type",
        ["All case types"] + available_case_types,
        key="turning_case_type",
    )

    # The selected case controls the analytical detail views.
    case_detail_data = transition_filtered.copy()

    if selected_case != "All case types":
        case_detail_data = case_detail_data[
            case_detail_data["CaseType"] == selected_case
        ].copy()

    if case_detail_data.empty:
        st.warning("No turning-point cases match the selected filters.")
    else:
        unique_case_matches = physical_matches(case_detail_data)

        # Correctness: averages are calculated at physical-match level,
        # not over duplicated team-perspective rows.
        unique_matches_count = int(
            unique_case_matches["MatchID"].nunique()
        )
        case_records_count = int(len(case_detail_data))
        average_swing = float(
            unique_case_matches["SwingIntensity"].mean()
        )
        average_goals = float(
            unique_case_matches["TotalMatchGoals"].mean()
        )

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric(
            "Unique matches",
            f"{unique_matches_count:,}",
        )

        kpi2.metric(
            "Case records",
            f"{case_records_count:,}",
            help=(
                "Cases are represented from each team's perspective. "
                "One physical match may therefore contribute two records."
            ),
        )

        kpi3.metric(
            "Average swing intensity",
            f"{average_swing:.2f}",
            help=(
                "Calculated once per unique MatchID so duplicate team "
                "perspectives do not receive extra weight."
            ),
        )

        kpi4.metric(
            "Average goals per match",
            f"{average_goals:.2f}",
            help=(
                "Calculated once per unique MatchID."
            ),
        )

        overview_col, density_col = st.columns([0.92, 1.18])

        # -------------------------------------------------------------
        # Case-type overview — always preserve all categories as context
        # -------------------------------------------------------------
        with overview_col:
            st.subheader("How common is each turning point?")

            count_rows = []

            for case_type in available_case_types:
                case_subset = transition_filtered[
                    transition_filtered["CaseType"] == case_type
                ]

                count_rows.append(
                    {
                        "CaseType": case_type,
                        "UniqueMatches": int(
                            case_subset["MatchID"].nunique()
                        ),
                    }
                )

            case_counts = pd.DataFrame(count_rows)

            case_counts["CaseType"] = pd.Categorical(
                case_counts["CaseType"],
                categories=available_case_types,
                ordered=True,
            )
            case_counts = case_counts.sort_values("CaseType")

            colors = []
            opacities = []

            for case_type in case_counts["CaseType"].astype(str):
                if selected_case == "All case types":
                    colors.append(
                        CASE_COLORS.get(case_type, "#7CB9E8")
                    )
                    opacities.append(1.0)
                elif case_type == selected_case:
                    colors.append(
                        CASE_COLORS.get(case_type, "#7CB9E8")
                    )
                    opacities.append(1.0)
                else:
                    colors.append("#59616E")
                    opacities.append(0.55)

            max_count = max(
                float(case_counts["UniqueMatches"].max()),
                1.0,
            )

            count_chart = go.Figure(
                go.Bar(
                    x=case_counts["UniqueMatches"],
                    y=case_counts["CaseType"].astype(str),
                    orientation="h",
                    marker=dict(
                        color=colors,
                        opacity=opacities,
                    ),
                    text=[
                        f"{value:,}"
                        for value in case_counts["UniqueMatches"]
                    ],
                    textposition="outside",
                    cliponaxis=False,
                    customdata=case_counts[
                        ["CaseType"]
                    ].values,
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Unique matches: %{x:,}"
                        "<extra></extra>"
                    ),
                )
            )

            count_chart.update_layout(
                height=410,
                showlegend=False,
                margin=dict(
                    l=20,
                    r=72,
                    t=10,
                    b=20,
                ),
                xaxis=dict(
                    title="Unique matches",
                    range=[0, max_count * 1.18],
                    rangemode="tozero",
                ),
                yaxis=dict(
                    title="",
                    autorange="reversed",
                ),
            )

            st.plotly_chart(
                count_chart,
                width="stretch",
                config={"displayModeBar": False},
            )

            if selected_case != "All case types":
                st.caption(
                    f"All four case types remain visible for context; "
                    f"**{selected_case}** controls the detail views."
                )

        # -------------------------------------------------------------
        # Unique-match density heatmap
        # -------------------------------------------------------------
        with density_col:
            st.subheader("Where do these matches cluster?")

            density_scope = (
                "all turning-point matches"
                if selected_case == "All case types"
                else selected_case.lower()
            )

            st.caption(
                f"Density of {density_scope} by total match shots and goals. "
                "Color encodes the number of unique physical matches."
            )

            turning_density_chart = make_density_heatmap(
                unique_case_matches,
                x_column="TotalMatchShots",
                y_column="TotalMatchGoals",
                x_title="Total match shots",
                y_title="Total match goals",
                height=410,
            )

            st.plotly_chart(
                turning_density_chart,
                width="stretch",
                config={"displayModeBar": False},
            )

        # -------------------------------------------------------------
        # Most dramatic case + details on demand
        # -------------------------------------------------------------
        sorted_case_records = case_detail_data.sort_values(
            [
                "SwingIntensity",
                "TotalMatchGoals",
                "TotalMatchShots",
            ],
            ascending=False,
        )

        top_case = sorted_case_records.iloc[0]

        quiet_insight(
            "Most dramatic case",
            (
                f"{top_case['Team']} vs {top_case['Opponent']} "
                f"({top_case['Season']}) — {top_case['CaseType']}. "
                f"The score changed from {top_case['HalfTimeScore']} "
                f"at halftime to {top_case['FullTimeScore']} at full time, "
                f"with swing intensity {float(top_case['SwingIntensity']):.1f}."
            ),
        )

        with st.expander(
            "View top dramatic case records",
            expanded=False,
        ):
            table_data = sorted_case_records.head(20)

            display_columns = [
                "Date",
                "Season",
                "League",
                "Team",
                "Opponent",
                "Venue",
                "CaseType",
                "HalfTimeScore",
                "FullTimeScore",
                "SwingIntensity",
                "TotalMatchGoals",
                "TotalMatchShots",
                "TotalMatchCards",
            ]

            display_names = {
                "Date": "Date",
                "Season": "Season",
                "League": "League",
                "Team": "Team",
                "Opponent": "Opponent",
                "Venue": "Venue",
                "CaseType": "Case type",
                "HalfTimeScore": "HT score",
                "FullTimeScore": "FT score",
                "SwingIntensity": "Swing",
                "TotalMatchGoals": "Goals",
                "TotalMatchShots": "Shots",
                "TotalMatchCards": "Cards",
            }

            st.dataframe(
                table_data[display_columns].rename(
                    columns=display_names
                ),
                width="stretch",
                hide_index=True,
                height=420,
            )


# =====================================================================
# TAB 2 — Outlier explorer
# =====================================================================
with outlier_tab:
    st.subheader("Statistical outlier explorer")
    st.markdown(
        """
        <div class="case-guidance">
            Each outlier category ranks the same match population by a different
            measure. The distribution view shows where the highest-ranked matches
            sit relative to the full evaluated population.
        </div>
        """,
        unsafe_allow_html=True,
    )

    available_outlier_types = [
        outlier_type
        for outlier_type in OUTLIER_ORDER
        if outlier_type in set(
            outlier_filtered["CaseType"].dropna().unique()
        )
    ]

    if not available_outlier_types:
        st.warning("No outlier records match the selected filters.")
    else:
        selected_outlier_type = st.selectbox(
            "Outlier measure",
            available_outlier_types,
            key="outlier_measure",
        )

        selected_outliers = outlier_filtered[
            outlier_filtered["CaseType"]
            == selected_outlier_type
        ].drop_duplicates(
            subset=["MatchID"]
        ).copy()

        if selected_outliers.empty:
            st.warning("No outliers match the selected filters.")
        else:
            selected_outliers["MatchLabel"] = (
                selected_outliers.apply(
                    format_match_label,
                    axis=1,
                )
            )

            metric_label = OUTLIER_LABELS.get(
                selected_outlier_type,
                "Rank value",
            )

            if selected_outlier_type == "Most Shots with Few Goals":
                st.caption(
                    "This category ranks matches identified in the prepared "
                    "outlier data as having unusually many shots relative to "
                    "their scoring output."
                )

            rank_values = (
                selected_outliers["CaseRankMetric"]
                .astype(float)
                .dropna()
            )

            matches_evaluated = int(
                selected_outliers["MatchID"].nunique()
            )
            maximum_value = float(rank_values.max())
            percentile_95 = float(
                rank_values.quantile(0.95)
            )
            median_value = float(
                rank_values.median()
            )

            o1, o2, o3, o4 = st.columns(4)

            o1.metric(
                "Matches evaluated",
                f"{matches_evaluated:,}",
            )
            o2.metric(
                "Maximum",
                display_number(maximum_value),
                help=metric_label,
            )
            o3.metric(
                "95th percentile",
                display_number(percentile_95),
                help=(
                    f"95% of evaluated matches have a {metric_label.lower()} "
                    "at or below this value."
                ),
            )
            o4.metric(
                "Median",
                display_number(median_value),
                help=metric_label,
            )

            ranking_col, landscape_col = st.columns(
                [0.94, 1.16]
            )

            # ---------------------------------------------------------
            # Ranked top matches
            # ---------------------------------------------------------
            with ranking_col:
                st.subheader("Which matches are most extreme?")

                top_matches = (
                    selected_outliers.nlargest(
                        10,
                        "CaseRankMetric",
                    )
                    .sort_values(
                        "CaseRankMetric",
                        ascending=True,
                    )
                    .reset_index(drop=True)
                    .copy()
                )

                # A categorical y-axis can collapse different physical matches
                # that happen to share the same score label. Numeric row positions
                # guarantee that every ranked match receives its own visible bar.
                top_matches["RankRow"] = list(
                    range(len(top_matches))
                )
                top_matches["DisplayLabel"] = (
                    top_matches["MatchLabel"].astype(str)
                    + " · "
                    + top_matches["Season"].astype(str)
                )

                bar_colors = [
                    "#78C6FF"
                    if float(value) == maximum_value
                    else "#3F6F97"
                    for value in top_matches["CaseRankMetric"]
                ]

                ranking_chart = go.Figure(
                    go.Bar(
                        x=top_matches["CaseRankMetric"],
                        y=top_matches["RankRow"],
                        orientation="h",
                        marker=dict(
                            color=bar_colors,
                        ),
                        text=[
                            display_number(value)
                            for value in top_matches[
                                "CaseRankMetric"
                            ]
                        ],
                        textposition="outside",
                        cliponaxis=False,
                        customdata=top_matches[
                            [
                                "MatchLabel",
                                "Season",
                                "League",
                                "HalfTimeScore",
                                "FullTimeScore",
                            ]
                        ].values,
                        hovertemplate=(
                            "<b>%{customdata[0]}</b><br>"
                            "Season: %{customdata[1]}<br>"
                            "League: %{customdata[2]}<br>"
                            "HT: %{customdata[3]}<br>"
                            "FT: %{customdata[4]}<br>"
                            f"{metric_label}: %{{x:.1f}}"
                            "<extra></extra>"
                        ),
                    )
                )

                rank_max = max(
                    float(
                        top_matches[
                            "CaseRankMetric"
                        ].max()
                    ),
                    1.0,
                )

                ranking_chart.update_layout(
                    height=470,
                    showlegend=False,
                    margin=dict(
                        l=20,
                        r=65,
                        t=15,
                        b=20,
                    ),
                    xaxis=dict(
                        title=metric_label,
                        range=[0, rank_max * 1.15],
                        rangemode="tozero",
                    ),
                    yaxis=dict(
                        title="",
                        tickmode="array",
                        tickvals=top_matches["RankRow"],
                        ticktext=top_matches["DisplayLabel"],
                    ),
                )

                st.plotly_chart(
                    ranking_chart,
                    width="stretch",
                    config={"displayModeBar": False},
                )

            # ---------------------------------------------------------
            # Density population + highlighted top outliers
            # ---------------------------------------------------------
            with landscape_col:
                st.subheader(
                    "Where do the extremes sit relative to normal matches?"
                )

                st.caption(
                    "The heatmap shows the full evaluated match population; "
                    "orange markers highlight the top 10 matches for the "
                    "selected outlier measure."
                )

                landscape_chart = make_density_heatmap(
                    selected_outliers,
                    x_column="TotalShots",
                    y_column="TotalGoals",
                    x_title="Total shots",
                    y_title="Total goals",
                    height=470,
                )

                top_overlay = selected_outliers.nlargest(
                    10,
                    "CaseRankMetric",
                ).copy()

                landscape_chart.add_trace(
                    go.Scatter(
                        x=top_overlay["TotalShots"],
                        y=top_overlay["TotalGoals"],
                        mode="markers",
                        marker=dict(
                            size=13,
                            color="#F4A261",
                            line=dict(
                                color="white",
                                width=1.4,
                            ),
                        ),
                        customdata=top_overlay[
                            [
                                "MatchLabel",
                                "Season",
                                "League",
                                "HalfTimeScore",
                                "FullTimeScore",
                                "CaseRankMetric",
                                "TotalCards",
                            ]
                        ].values,
                        hovertemplate=(
                            "<b>%{customdata[0]}</b><br>"
                            "Season: %{customdata[1]}<br>"
                            "League: %{customdata[2]}<br>"
                            "HT: %{customdata[3]}<br>"
                            "FT: %{customdata[4]}<br>"
                            f"{metric_label}: %{{customdata[5]:.1f}}<br>"
                            "Shots: %{x:.0f}<br>"
                            "Goals: %{y:.0f}<br>"
                            "Cards: %{customdata[6]:.0f}"
                            "<extra></extra>"
                        ),
                        name="Top 10",
                        showlegend=False,
                    )
                )

                # Label only the single highest-ranked match.
                # The ranking chart already identifies all top-10 matches,
                # so extra static labels here would duplicate information
                # and can overlap when extreme matches share similar values.
                top_one = selected_outliers.nlargest(
                    1,
                    "CaseRankMetric",
                ).iloc[0]

                landscape_chart.add_annotation(
                    x=float(top_one["TotalShots"]),
                    y=float(top_one["TotalGoals"]),
                    text=str(top_one["MatchLabel"]),
                    showarrow=True,
                    arrowhead=0,
                    ax=18,
                    ay=-18,
                    font=dict(
                        size=10,
                        color="#F4A261",
                    ),
                    arrowcolor="#F4A261",
                    bgcolor="rgba(15,18,25,0.78)",
                    borderpad=2,
                )

                st.plotly_chart(
                    landscape_chart,
                    width="stretch",
                    config={"displayModeBar": False},
                )

            # ---------------------------------------------------------
            # Outlier insight + details on demand
            # ---------------------------------------------------------
            strongest_outlier = selected_outliers.nlargest(
                1,
                "CaseRankMetric",
            ).iloc[0]

            quiet_insight(
                OUTLIER_INSIGHT_LABELS.get(
                    selected_outlier_type,
                    "Top outlier",
                ),
                (
                    f"{strongest_outlier['HomeTeam']} vs "
                    f"{strongest_outlier['AwayTeam']} finished "
                    f"{strongest_outlier['FullTimeScore']} after a halftime "
                    f"score of {strongest_outlier['HalfTimeScore']}. "
                    f"Its {metric_label.lower()} was "
                    f"{float(strongest_outlier['CaseRankMetric']):.1f}."
                ),
            )

            with st.expander(
                "View ranked match details",
                expanded=False,
            ):
                outlier_table = selected_outliers.sort_values(
                    "CaseRankMetric",
                    ascending=False,
                ).head(25)

                outlier_columns = [
                    "Date",
                    "Season",
                    "League",
                    "HomeTeam",
                    "AwayTeam",
                    "HalfTimeScore",
                    "FullTimeScore",
                    "MatchTransition",
                    "SwingIntensity",
                    "TotalGoals",
                    "TotalShots",
                    "TotalCards",
                    "CaseRankMetric",
                ]

                outlier_names = {
                    "Date": "Date",
                    "Season": "Season",
                    "League": "League",
                    "HomeTeam": "Home team",
                    "AwayTeam": "Away team",
                    "HalfTimeScore": "HT score",
                    "FullTimeScore": "FT score",
                    "MatchTransition": "Transition",
                    "SwingIntensity": "Swing",
                    "TotalGoals": "Goals",
                    "TotalShots": "Shots",
                    "TotalCards": "Cards",
                    "CaseRankMetric": "Rank value",
                }

                st.dataframe(
                    outlier_table[outlier_columns].rename(
                        columns=outlier_names
                    ),
                    width="stretch",
                    hide_index=True,
                    height=440,
                )