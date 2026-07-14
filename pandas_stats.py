"""
pandas_stats.py

Same analysis as pure_python_stats.py, using pandas.
Kept intentionally close to that script's structure so the two are easy
to diff against each other.
"""

import ast
import pandas as pd

CSV_PATH = "fb_ads_president_scored_anon.csv"  # place the downloaded file next to this script

RANGE_COLUMNS = ["estimated_audience_size", "impressions", "spend"]
DATE_COLUMNS = ["ad_creation_time", "ad_delivery_start_time", "ad_delivery_stop_time"]


def parse_range_midpoint(value):
    """Same treatment as the pure-Python script: midpoint of lower/upper_bound,
    or lower_bound alone when upper_bound is absent (open-ended range)."""
    if pd.isna(value):
        return None
    try:
        d = ast.literal_eval(value)
        lo = float(d["lower_bound"])
        if "upper_bound" in d:
            hi = float(d["upper_bound"])
            return (lo + hi) / 2
        return lo
    except (ValueError, SyntaxError, TypeError, KeyError):
        return None


def load_data(path):
    df = pd.read_csv(path)
    for col in RANGE_COLUMNS:
        df[col + "_mid"] = df[col].apply(parse_range_midpoint)
    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def main():
    df = load_data(CSV_PATH)

    print("=" * 80)
    print("SHAPE & STRUCTURE")
    print("=" * 80)
    print("Shape:", df.shape)
    print()
    df.info()
    print()

    print("=" * 80)
    print("MISSING VALUES")
    print("=" * 80)
    missing = df.isna().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    print(pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct}))
    print()

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    print("=" * 80)
    print("NUMERIC SUMMARY (describe)")
    print("=" * 80)
    print(df[numeric_cols].describe())
    print()

    print("=" * 80)
    print("CATEGORICAL SUMMARY (describe)")
    print("=" * 80)
    print(df[categorical_cols].describe())
    print()

    print("=" * 80)
    print("PER-COLUMN VALUE COUNTS (categorical, top 5)")
    print("=" * 80)
    for col in categorical_cols:
        print(f"\n--- {col} ---")
        print(f"nunique: {df[col].nunique()}")
        print(df[col].value_counts().head(5))


if __name__ == "__main__":
    main()