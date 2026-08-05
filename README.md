# Football Turning Points

Streamlit visualization project examining halftime-to-full-time transitions
across the English Premier League, Spanish La Liga, Italian Serie A,
German Bundesliga, and French Ligue 1 from 2015/16 through 2024/25.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Current pages

1. League Transition Overview
2. Team Performance Explorer
3. Match Cases and Outliers

The application uses nine processed CSV tables derived from the same
original football match dataset used in the Tableau prototype.
