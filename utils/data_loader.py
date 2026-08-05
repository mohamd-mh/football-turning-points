from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    return pd.read_csv(path)


def weighted_average(
    frame: pd.DataFrame,
    value_column: str,
    weight_column: str,
) -> float:
    valid = frame[[value_column, weight_column]].dropna()
    if valid.empty or valid[weight_column].sum() == 0:
        return 0.0
    return float(
        (valid[value_column] * valid[weight_column]).sum()
        / valid[weight_column].sum()
    )
