Football Turning Points

Interactive football visualization project analyzing how matches change between halftime and full time across Europe’s five major leagues from 2015/16 through 2024/25.

Live Application

Streamlit app: https://football-turning-points.streamlit.app

Main Research Question

How do European football teams protect leads, recover from deficits, break halftime draws, and experience volatile second halves across leagues and seasons?

The application is designed to move from broad patterns to detailed evidence: first comparing leagues, then examining individual teams, and finally inspecting turning-point matches and statistical outliers.

Dataset at a Glance

18,008 matches

5 leagues

10 seasons

160 teams

976 team-season records

Seasons covered: 2015/16–2024/25

Leagues:

English Premier League

Spanish La Liga

Italian Serie A

German Bundesliga

French Ligue 1

The deployed application uses nine processed CSV tables stored in the data/ directory.

Processed Data Tables

File

Purpose

01_transition_matrix_rates.csv

Halftime-to-full-time transition rates

02_league_season_metrics.csv

League metrics by season

03_league_metrics.csv

Overall league-level metrics

04_team_metrics.csv

Overall team-level metrics

05_team_season_metrics.csv

Team metrics by season

06_home_away_metrics.csv

Home-versus-away team performance

07_opponent_transition_rates.csv

Opponent-based transition metrics

08_team_transition_cases.csv

Turning-point match cases from the team perspective

09_match_outlier_cases.csv

Match-level outlier rankings

Preprocessing

The original match data was transformed into analysis-ready tables before being loaded by the web application. The preprocessing stage included:

combining match records across leagues and seasons;

standardizing league, season, team, score, and match identifiers;

deriving halftime and full-time match states;

calculating league-, team-, season-, and venue-level aggregate metrics;

calculating halftime-to-full-time transition rates;

generating turning-point categories such as comeback wins, recovery draws, draw breakthroughs, and lead collapses;

preparing unique-match identifiers so match-level statistics are not double-counted when a source table contains team-perspective records;

preparing match-level outlier categories used in the outlier explorer.

The application itself reads the processed tables rather than recalculating the full preprocessing pipeline at runtime.

Application Structure

1. League Overview

Compares leagues and seasons using measures such as:

lead protection;

comeback ability;

match volatility;

scoring;

halftime-to-full-time outcome transitions.

The page combines KPI cards, temporal trends, league rankings, transition views, filters, and coordinated analytical focus.

2. Team Explorer

Allows the viewer to select a league and club and investigate:

long-term performance across seasons;

comparison with the league benchmark;

lead-protection and comeback behavior;

home-versus-away differences;

team position relative to league peers.

3. Match Cases

Moves from aggregate patterns to individual match evidence.

The page contains two analytical views:

Turning-point cases — comeback wins, recovery draws, draw breakthroughs, and lead collapses.

Outlier explorer — extreme matches ranked by swing intensity, scoring, cards, and shots with few goals.

Match-level KPIs and density views use unique match identifiers to avoid double-counting physical matches represented by more than one team-perspective record.

Interaction Design

The visualization uses interaction only where it supports an analytical task. Examples include:

league and season filters;

team selection;

metric selectors;

turning-point and outlier selectors;

coordinated views;

hover tooltips with exact values and match details;

tabs for alternative analytical perspectives;

details-on-demand through expandable tables.

The goal is to preserve context while allowing the viewer to move from overview to comparison and then to individual cases.

Key Terms

Lead protection: percentage of halftime leads that remain wins at full time.

Comeback win: a team trails at halftime but finishes as the winner.

Recovery draw: a team trails at halftime but recovers to finish level.

Draw breakthrough: a team is level at halftime and converts the match into a win.

Lead collapse: a team leads at halftime but finishes with a loss.

Match volatility: the extent to which the score or match state changes after halftime.

Technologies

Python

Streamlit

Pandas

Plotly

HTML/CSS

Git

GitHub

Streamlit Community Cloud

Project Structure

football-turning-points/
├── app.py
├── assets/
│   └── style.css
├── data/
│   ├── 01_transition_matrix_rates.csv
│   ├── 02_league_season_metrics.csv
│   ├── 03_league_metrics.csv
│   ├── 04_team_metrics.csv
│   ├── 05_team_season_metrics.csv
│   ├── 06_home_away_metrics.csv
│   ├── 07_opponent_transition_rates.csv
│   ├── 08_team_transition_cases.csv
│   └── 09_match_outlier_cases.csv
├── pages/
│   ├── 1_League_Overview.py
│   ├── 2_Team_Explorer.py
│   └── 3_Match_Cases.py
├── utils/
│   ├── __init__.py
│   └── data_loader.py
├── requirements.txt
└── README.md

Run Locally

python -m venv .venv

Windows PowerShell

.\.venv\Scripts\Activate.ps1

Git Bash

source .venv/Scripts/activate

Install dependencies:

python -m pip install -r requirements.txt

Run the application:

python -m streamlit run app.py

Then open the local Streamlit URL shown in the terminal.

Deployment

The public application is deployed with Streamlit Community Cloud from the GitHub repository.

Purpose

The project turns thousands of match records into an interactive analytical workflow. Instead of manually searching rows, the viewer can compare leagues, identify long-term patterns, benchmark clubs, investigate venue effects, and trace unusual aggregate behavior back to the individual matches that produced it.