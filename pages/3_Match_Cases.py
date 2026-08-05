from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import load_csv


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

transition_cases = load_csv("08_team_transition_cases.csv")
outlier_cases = load_csv("09_match_outlier_cases.csv")

CASE_COLORS = {
    "Comeback Win": "#5CD6A0",
    "Recovery Draw": "#7CB9E8",
    "Draw Breakthrough": "#F4A261",
    "Lead Collapse": "#FF6B6B",
}

OUTLIER_LABELS = {
    "Highest Swing Intensity": "Swing intensity",
    "Highest Total Goals": "Total goals",
    "Highest Total Shots": "Total shots",
    "Highest Total Cards": "Total cards",
}


def format_match_label(row: pd.Series) -> str:
    return (
        f"{row['HomeTeam']} {row['FullTimeScore']} "
        f"{row['AwayTeam']}"
    )


st.title("🔎 Match Cases and Outliers")
st.caption(
    "Move from aggregate patterns to the individual matches that produced "
    "comebacks, collapses, breakthroughs, and statistical extremes."
)

all_leagues = sorted(transition_cases["League"].dropna().unique())
all_seasons = sorted(
    transition_cases["Season"].dropna().astype(str).unique()
)

with st.sidebar:
    st.header("Global filters")

    selected_league = st.selectbox(
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
        "Both tabs use the same league and season range."
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

transition_tab, outlier_tab = st.tabs(
    ["Turning-point cases", "Outlier explorer"]
)

with transition_tab:
    st.subheader("Halftime turning-point cases")
    st.caption(
        "Each row represents a team’s perspective in a match. "
        "A single match may therefore appear as both a comeback and a collapse."
    )

    case_options = sorted(
        transition_filtered["CaseType"].dropna().unique()
    )
    selected_case = st.selectbox(
        "Case type",
        ["All case types"] + case_options,
        key="transition_case_type",
    )

    case_data = transition_filtered.copy()
    if selected_case != "All case types":
        case_data = case_data[
            case_data["CaseType"] == selected_case
        ].copy()

    if case_data.empty:
        st.warning("No turning-point cases match the selected filters.")
    else:
        unique_matches = case_data["MatchID"].nunique()
        team_perspectives = len(case_data)
        average_swing = case_data["SwingIntensity"].mean()
        average_goals = case_data["TotalMatchGoals"].mean()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Unique matches", f"{unique_matches:,}")
        kpi2.metric(
            "Team perspectives",
            f"{team_perspectives:,}",
            help=(
                "A match can appear from both teams’ perspectives when one "
                "team completes a comeback and the opponent collapses."
            ),
        )
        kpi3.metric("Average swing", f"{average_swing:.2f}")
        kpi4.metric("Average match goals", f"{average_goals:.2f}")

        chart_left, chart_right = st.columns([0.9, 1.25])

        with chart_left:
            st.markdown("#### Cases by type")

            case_counts = (
                case_data.groupby("CaseType", as_index=False)
                .agg(UniqueMatches=("MatchID", "nunique"))
                .sort_values("UniqueMatches", ascending=True)
            )

            count_chart = px.bar(
                case_counts,
                x="UniqueMatches",
                y="CaseType",
                orientation="h",
                color="CaseType",
                color_discrete_map=CASE_COLORS,
                labels={
                    "UniqueMatches": "Unique matches",
                    "CaseType": "",
                },
                text="UniqueMatches",
            )

            count_chart.update_traces(
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Unique matches: %{x:,}"
                    "<extra></extra>"
                ),
            )

            count_chart.update_layout(
                height=430,
                showlegend=False,
                margin=dict(l=20, r=45, t=20, b=20),
            )

            st.plotly_chart(
                count_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with chart_right:
            st.markdown("#### Goals and shots behind the cases")

            scatter_data = case_data.drop_duplicates(
                subset=["MatchID", "CaseType", "Team"]
            ).copy()

            scatter_chart = px.scatter(
                scatter_data,
                x="TotalMatchShots",
                y="TotalMatchGoals",
                color="CaseType",
                size="SwingIntensity",
                size_max=18,
                color_discrete_map=CASE_COLORS,
                hover_name="Team",
                hover_data={
                    "Opponent": True,
                    "Season": True,
                    "HalfTimeScore": True,
                    "FullTimeScore": True,
                    "TotalMatchCards": True,
                    "TotalMatchShots": ":.0f",
                    "TotalMatchGoals": ":.0f",
                    "SwingIntensity": ":.1f",
                    "CaseType": False,
                },
                labels={
                    "TotalMatchShots": "Total match shots",
                    "TotalMatchGoals": "Total match goals",
                    "CaseType": "Case type",
                },
            )

            scatter_chart.update_layout(
                height=430,
                legend_title_text="Case type",
                margin=dict(l=20, r=20, t=20, b=20),
            )

            st.plotly_chart(
                scatter_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        st.markdown("#### Most dramatic cases")

        table_data = case_data.sort_values(
            [
                "SwingIntensity",
                "TotalMatchGoals",
                "TotalMatchShots",
            ],
            ascending=False,
        ).head(20)

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
            use_container_width=True,
            hide_index=True,
            height=420,
        )

        top_case = table_data.iloc[0]
        st.info(
            f"**Most dramatic case in this view:** "
            f"{top_case['Team']} against {top_case['Opponent']} "
            f"({top_case['Season']}), changing from "
            f"{top_case['HalfTimeScore']} at halftime to "
            f"{top_case['FullTimeScore']} at full time."
        )

with outlier_tab:
    st.subheader("Statistical outlier explorer")
    st.caption(
        "Each outlier category ranks the same match dataset by a different "
        "measure. The chart uses one record per unique match."
    )

    outlier_types = sorted(
        outlier_filtered["CaseType"].dropna().unique()
    )

    selected_outlier_type = st.selectbox(
        "Outlier measure",
        outlier_types,
        key="outlier_case_type",
    )

    selected_outliers = outlier_filtered[
        outlier_filtered["CaseType"] == selected_outlier_type
    ].drop_duplicates(subset=["MatchID"]).copy()

    if selected_outliers.empty:
        st.warning("No outliers match the selected filters.")
    else:
        selected_outliers["MatchLabel"] = selected_outliers.apply(
            format_match_label,
            axis=1,
        )

        unique_outlier_matches = selected_outliers["MatchID"].nunique()
        maximum_rank = selected_outliers["CaseRankMetric"].max()
        average_outlier_goals = selected_outliers["TotalGoals"].mean()
        average_outlier_shots = selected_outliers["TotalShots"].mean()

        o1, o2, o3, o4 = st.columns(4)
        o1.metric("Unique matches", f"{unique_outlier_matches:,}")
        o2.metric(
            f"Maximum {OUTLIER_LABELS.get(selected_outlier_type, 'value').lower()}",
            f"{maximum_rank:,.1f}",
        )
        o3.metric("Average goals", f"{average_outlier_goals:.2f}")
        o4.metric("Average shots", f"{average_outlier_shots:.1f}")

        top_matches = selected_outliers.nlargest(
            12,
            "CaseRankMetric",
        ).sort_values("CaseRankMetric", ascending=True)

        outlier_left, outlier_right = st.columns([1, 1.15])

        with outlier_left:
            st.markdown("#### Highest-ranked matches")

            ranking_chart = px.bar(
                top_matches,
                x="CaseRankMetric",
                y="MatchLabel",
                orientation="h",
                color="CaseRankMetric",
                color_continuous_scale=[
                    "#2D5F8B",
                    "#78C6FF",
                ],
                labels={
                    "CaseRankMetric": OUTLIER_LABELS.get(
                        selected_outlier_type,
                        "Rank value",
                    ),
                    "MatchLabel": "",
                },
            )

            ranking_chart.update_traces(
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Value: %{x:.1f}"
                    "<extra></extra>"
                )
            )

            ranking_chart.update_layout(
                height=500,
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20),
            )

            st.plotly_chart(
                ranking_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with outlier_right:
            st.markdown("#### Match intensity landscape")

            intensity_chart = px.scatter(
                selected_outliers,
                x="TotalShots",
                y="TotalGoals",
                color="SwingIntensity",
                size="TotalCards",
                size_max=20,
                color_continuous_scale=[
                    "#172033",
                    "#2D5F8B",
                    "#78C6FF",
                ],
                hover_name="MatchLabel",
                hover_data={
                    "Season": True,
                    "League": True,
                    "HalfTimeScore": True,
                    "MatchTransition": True,
                    "TotalShots": ":.0f",
                    "TotalGoals": ":.0f",
                    "TotalCards": ":.0f",
                    "SwingIntensity": ":.1f",
                },
                labels={
                    "TotalShots": "Total shots",
                    "TotalGoals": "Total goals",
                    "SwingIntensity": "Swing intensity",
                    "TotalCards": "Cards",
                },
            )

            intensity_chart.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=20, b=20),
            )

            st.plotly_chart(
                intensity_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        st.markdown("#### Ranked match details")

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
            use_container_width=True,
            hide_index=True,
            height=440,
        )

        strongest_outlier = outlier_table.iloc[0]

        st.info(
            f"**Top outlier:** {strongest_outlier['HomeTeam']} versus "
            f"{strongest_outlier['AwayTeam']} ended "
            f"{strongest_outlier['FullTimeScore']} after a halftime score of "
            f"{strongest_outlier['HalfTimeScore']}. Its "
            f"{OUTLIER_LABELS.get(selected_outlier_type, 'rank value').lower()} "
            f"was {strongest_outlier['CaseRankMetric']:.1f}."
        )