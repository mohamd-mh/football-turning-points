# ⚽ Football Turning Points

**Interactive visualization of halftime → full-time match dynamics across Europe’s five major football leagues.**

> **Research question:** How do European football teams protect leads, recover from deficits, break halftime draws, and experience volatile second halves across leagues and seasons?

### 🌐 [Open the Live Streamlit Application](https://football-turning-points.streamlit.app)

---

## 📊 Dataset at a Glance

| Metric | Value |
|---|---:|
| Matches | **18,008** |
| Leagues | **5** |
| Seasons | **10** |
| Teams | **160** |
| Team-season records | **976** |
| Coverage | **2015/16–2024/25** |

**Leagues:** English Premier League · Spanish La Liga · Italian Serie A · German Bundesliga · French Ligue 1

---

## 🧭 Analysis Workflow

The project follows an **overview → comparison → detail** structure.

### 📈 League Overview

Compare leagues and seasons through:

- lead-protection rate;
- comeback-win rate;
- scoring and volatility;
- seasonal trends;
- halftime → full-time transitions.

**Interactions:** league and season filters, metric selection, coordinated views, and hover details.

### 🛡️ Team Explorer

Select a league and club to examine:

- performance across seasons;
- comparison with league benchmarks;
- lead protection and comeback behavior;
- home-versus-away differences;
- the club’s position relative to league peers.

**Interactions:** league/team selectors, metric selectors, analytical tabs, and benchmark comparisons.

### 🔎 Match Cases & Outliers

Move from aggregate patterns to the individual matches behind them.

**Turning-point cases**

- Comeback Win
- Recovery Draw
- Draw Breakthrough
- Lead Collapse

**Statistical outliers**

- Highest Swing Intensity
- Highest-Scoring Matches
- Most Cards
- Most Shots with Few Goals

**Interactions:** filters, case/outlier selectors, hover tooltips, density views, rankings, and details-on-demand.

---

## 🔄 Core Match-State Concepts

| Concept | Definition |
|---|---|
| **Lead protection** | Percentage of halftime leads that remain wins at full time |
| **Comeback win** | A team trails at halftime and finishes as the winner |
| **Recovery draw** | A team trails at halftime and recovers to finish level |
| **Draw breakthrough** | A team is level at halftime and converts the match into a win |
| **Lead collapse** | A team leads at halftime but finishes with a loss |
| **Match volatility** | Extent to which the score or match state changes after halftime |

---

## 💡 Why This Visualization Is Useful

The source data contains thousands of match records. Manually reading rows makes league comparisons, long-term trends, team behavior, venue effects, and exceptional matches difficult to identify.

The application turns those records into an analytical workflow:

**compare → filter → focus → inspect → verify**

This allows the viewer to move from broad patterns to the individual matches that produced them.

---

## 🧹 Data Preparation

The deployed application uses processed analysis-ready CSV tables. Preparation included:

1. combining match records across leagues and seasons;
2. standardizing league, season, team, score, and match identifiers;
3. deriving halftime and full-time match states;
4. calculating league-, team-, season-, and venue-level metrics;
5. calculating halftime-to-full-time transition rates;
6. generating turning-point categories;
7. using unique match identifiers to prevent double-counting team-perspective records;
8. preparing match-level outlier rankings.

---

## 🗂️ Processed Data Tables

| File | Purpose |
|---|---|
| `01_transition_matrix_rates.csv` | Halftime → full-time transition rates |
| `02_league_season_metrics.csv` | League metrics by season |
| `03_league_metrics.csv` | Overall league metrics |
| `04_team_metrics.csv` | Overall team metrics |
| `05_team_season_metrics.csv` | Team metrics by season |
| `06_home_away_metrics.csv` | Home-versus-away performance |
| `07_opponent_transition_rates.csv` | Opponent-based transition rates |
| `08_team_transition_cases.csv` | Turning-point match cases |
| `09_match_outlier_cases.csv` | Match-level outlier rankings |

---

## 🛠️ Technology Stack

- **Python**
- **Pandas**
- **Plotly**
- **Streamlit**
- **HTML / CSS**
- **Git & GitHub**
- **Streamlit Community Cloud**

---

## 📁 Project Structure

```text
football-turning-points/
├── app.py
├── requirements.txt
├── README.md
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
└── utils/
    ├── __init__.py
    └── data_loader.py
```

---

## ▶️ Run Locally

```bash
git clone https://github.com/mohamd-mh/football-turning-points.git
cd football-turning-points

python -m venv .venv
source .venv/Scripts/activate

python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 🌐 Deployment

The public application is deployed from this GitHub repository using **Streamlit Community Cloud**.

**Live application:** https://football-turning-points.streamlit.app

---

**Football Turning Points — from halftime state, to full-time outcome, to the match behind the pattern.**
