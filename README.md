# Task 01: Descriptive Statistics — 2024 Facebook Presidential Ad Spending

## Project Description
This project explores real Facebook ad purchases from the 2024 U.S. Presidential
election. It computes descriptive statistics two independent ways — once using
only Python's standard library, once using Pandas — to compare a manual,
first-principles approach against a library-driven one.

## Dataset
Source: [2024 Facebook Political Ads (Google Drive)](https://drive.google.com/drive/folders/1e9FnDRyA-MWt_wLQHCctS5Dw60iC87oW?usp=sharing)

Download `fb_ads_president_scored_anon.csv` and place it in the project root
(or update `CSV_PATH` in both scripts). The dataset is **not** included in
this repo.

The file has 246,745 rows and 40 columns. Each row is one ad purchase by an
organization whose ad mentions at least one presidential candidate.

## How to Run

```bash
pip install -r requirements.txt

python pure_python_stats.py
python pandas_stats.py
```

No arguments needed — both scripts read `fb_ads_president_scored_anon.csv`
from the working directory.

## A note on `spend` / `impressions` / `estimated_audience_size`
Meta reports these as ranges (e.g. `{'lower_bound': '200', 'upper_bound': '299'}`),
not exact numbers. Both scripts take the **midpoint** of each range as the
numeric value used for statistics — this is a deliberate simplification, not
a data artifact, and it's the same treatment in both scripts so the two stay
comparable.

## Findings & Comparison
See [FINDINGS.md](FINDINGS.md) and [COMPARISON.md](COMPARISON.md).