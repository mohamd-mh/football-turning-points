<div align="center">

⚽ Football Turning Points

Interactive visualization of halftime → full-time match dynamics

Explore how teams protect leads, recover from deficits, break halftime draws, and experience volatile second halves across Europe’s five major football leagues.






</div>

🎯 Research Question

How do European football teams protect leads, recover from deficits, break halftime draws, and experience volatile second halves across leagues and seasons?

The project is designed as an overview → comparison → detail analytical workflow.
A viewer can begin with league-level patterns, continue to team-level behavior, and finally inspect the individual matches behind unusual results.

📊 Dataset at a Glance

Metric

Value

Matches

18,008

Leagues

5

Seasons

10

Teams

160

Team-season records

976

Coverage

2015/16–2024/25

Leagues included

🏴 English Premier League

🇪🇸 Spanish La Liga

🇮🇹 Italian Serie A

🇩🇪 German Bundesliga

🇫🇷 French Ligue 1

🧭 Application Structure

The application contains three complementary analytical pages.

📈 1. League Overview

Compare league behavior across seasons.

Questions answered:

Which league protects halftime leads most effectively?

Which league produces more comeback wins?

How has match behavior changed over time?

Which leagues are more volatile?

What typically happens after different halftime states?

Main interactions: league filter, season range, metric selector, coordinated views, hover details.

🛡️ 2. Team Explorer

Examine one club relative to its league and across seasons.

Questions answered:

How has the team performed over time?

Is the team above or below its league benchmark?

How strong is its lead protection?

How often does it recover from deficits?

Does home versus away performance differ?

Main interactions: league selection, team selection, metric selectors, analytical tabs, benchmark comparisons.

🔎 3. Match Cases & Outliers

Move from aggregate patterns to the individual matches that produced them.

Turning-point cases

Comeback Win

Recovery Draw

Draw Breakthrough

Lead Collapse

Statistical outliers

Highest Swing Intensity

Highest-Scoring Matches

Most Cards

Most Shots with Few Goals

Main interactions: case selector, outlier selector, filters, hover details, density views, ranked tables, details-on-demand.

🔄 Core Match-State Concepts

Concept

Meaning

Lead protection

Percentage of halftime leads that remain wins at full time

Comeback win

A team trails at halftime and finishes as the winner

Recovery draw

A team trails at halftime and recovers to finish level

Draw breakthrough

A team is level at halftime and converts the match into a win

Lead collapse

A team leads at halftime but finishes with a loss

Match volatility

Extent to which the score or match state changes after halftime

💡 Why the Visualization Is Useful

The raw data contains thousands of match records. Reading rows manually makes it difficult to identify:

long-term league differences;

seasonal changes;

team-specific strengths and weaknesses;

home-versus-away effects;

unusual comeback or collapse patterns;

statistical outliers.

The application converts those records into an interactive visual workflow that lets the viewer:

compare → filter → focus → inspect → verify

rather than manually searching the dataset.

🧹 Data Preparation

The deployed application uses processed analysis-ready CSV files.

Main preprocessing tasks included:

Combining match records across leagues and seasons.

Standardizing league, season, team, score, and match identifiers.

Deriving halftime and full-time match states.

Calculating league-, team-, season-, and venue-level metrics.

Calculating halftime-to-full-time transition rates.

Creating turning-point categories.

Creating unique match identifiers to avoid double-counting team-perspective records.

Preparing match-level outlier rankings.

🗂️ Processed Data Files

File

Purpose

01_transition_matrix_rates.csv

Halftime → full-time transition rates

02_league_season_metrics.csv

League metrics by season

03_league_metrics.csv

Overall league metrics

04_team_metrics.csv

Overall team metrics

05_team_season_metrics.csv

Team metrics by season

06_home_away_metrics.csv

Home-versus-away performance

07_opponent_transition_rates.csv

Opponent-based transition rates

08_team_transition_cases.csv

Turning-point match cases

09_match_outlier_cases.csv

Match-level outlier rankings

🛠️ Technology Stack

Tool

Role

Python

Application and data logic

Pandas

Data loading and manipulation

Plotly

Interactive charts

Streamlit

Web application framework

HTML / CSS

Visual styling

Git + GitHub

Version control and project hosting

Streamlit Community Cloud

Public deployment

📁 Project Structure

football-turning-points/
│
├── app.py
├── requirements.txt
├── README.md
│
├── assets/
│   └── style.css
│
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
│
├── pages/
│   ├── 1_League_Overview.py
│   ├── 2_Team_Explorer.py
│   └── 3_Match_Cases.py
│
└── utils/
    ├── __init__.py
    └── data_loader.py

▶️ Run Locally

1. Clone the repository

git clone https://github.com/mohamd-mh/football-turning-points.git
cd football-turning-points

2. Create a virtual environment

python -m venv .venv

3. Activate it

Git Bash

source .venv/Scripts/activate

Windows PowerShell

.\.venv\Scripts\Activate.ps1

4. Install dependencies

python -m pip install -r requirements.txt

5. Start the application

python -m streamlit run app.py

🌐 Live Deployment

The application is publicly available here:

👉 football-turning-points.streamlit.app

The hosted version is deployed from the GitHub repository using Streamlit Community Cloud.

<div align="center">

Football Turning Points

From halftime state → to full-time outcome → to the match behind the pattern.

</div>