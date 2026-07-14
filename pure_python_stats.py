"""
pure_python_stats.py

Descriptive statistics for the 2024 FB Presidential ads dataset,
computed using ONLY the Python standard library (csv, math, collections).

Design notes:
- Single pass streaming (the file is ~110MB / 246k rows) with a small
  sample-based pre-pass to infer each column's type.
- estimated_audience_size / impressions / spend arrive as stringified
  range dicts, e.g. "{'lower_bound': '200', 'upper_bound': '299'}".
  We treat these as numeric by taking the midpoint of the range and
  flag them with type "range" so the report notes that choice.
  Some rows only report lower_bound with no upper_bound (an open-ended
  range, e.g. audience size "1,000,001+") — in that case we use
  lower_bound itself as the value.
"""

import csv
import math
import ast
import re
from collections import Counter

CSV_PATH = "fb_ads_president_scored_anon.csv"  # place the downloaded file next to this script
SAMPLE_SIZE = 2000
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan"}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def is_missing(value):
    return value is None or value.strip().lower() in MISSING_TOKENS


def try_parse_range_dict(value):
    """Parse "{'lower_bound': '10', 'upper_bound': '20'}" -> midpoint (15.0).
    Some rows only report lower_bound (open-ended range, e.g. '1,000,001+').
    In that case, use lower_bound itself as the value."""
    v = value.strip()
    if v.startswith("{") and "lower_bound" in v:
        try:
            d = ast.literal_eval(v)
            lo = float(d.get("lower_bound"))
            if "upper_bound" in d:
                hi = float(d.get("upper_bound"))
                return (lo + hi) / 2
            return lo  # open-ended range, no upper bound reported
        except (ValueError, SyntaxError, TypeError):
            return None
    return None


def try_parse_number(value):
    """Handles '$1,234.56', '12%', plain floats/ints. Returns None if not numeric."""
    v = value.strip().replace("$", "").replace(",", "").replace("%", "")
    try:
        return float(v)
    except ValueError:
        return None


def looks_like_date(value):
    return bool(DATE_RE.match(value.strip()))


def infer_column_types(path, columns):
    """Sample the first SAMPLE_SIZE rows to guess each column's type."""
    counts = {c: {"numeric": 0, "range": 0, "date": 0, "total": 0} for c in columns}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= SAMPLE_SIZE:
                break
            for c in columns:
                val = row[c]
                if is_missing(val):
                    continue
                counts[c]["total"] += 1
                if try_parse_range_dict(val) is not None:
                    counts[c]["range"] += 1
                elif try_parse_number(val) is not None:
                    counts[c]["numeric"] += 1
                elif looks_like_date(val):
                    counts[c]["date"] += 1

    types = {}
    for c, info in counts.items():
        total = info["total"] or 1
        if info["range"] / total > 0.8:
            types[c] = "range"
        elif info["numeric"] / total > 0.8:
            types[c] = "numeric"
        elif info["date"] / total > 0.8:
            types[c] = "date"
        else:
            types[c] = "categorical"
    return types


class NumericAccumulator:
    """Streams numeric values and computes count/mean/min/max/stdev/median from scratch."""

    def __init__(self):
        self.values = []  # kept in memory for median + sample stdev
        self.count = 0
        self.total = 0.0
        self.min = None
        self.max = None

    def add(self, x):
        self.values.append(x)
        self.count += 1
        self.total += x
        if self.min is None or x < self.min:
            self.min = x
        if self.max is None or x > self.max:
            self.max = x

    def mean(self):
        return self.total / self.count if self.count else None

    def stdev(self):
        """Sample standard deviation (n-1 denominator, matches pandas default)."""
        if self.count < 2:
            return 0.0
        m = self.mean()
        var = sum((x - m) ** 2 for x in self.values) / (self.count - 1)
        return math.sqrt(var)

    def median(self):
        if not self.count:
            return None
        s = sorted(self.values)
        mid = self.count // 2
        if self.count % 2 == 1:
            return s[mid]
        return (s[mid - 1] + s[mid]) / 2


class CategoricalAccumulator:
    """Streams string values and tracks frequency counts."""

    def __init__(self):
        self.counter = Counter()
        self.count = 0

    def add(self, x):
        self.counter[x] += 1
        self.count += 1

    def nunique(self):
        return len(self.counter)

    def mode(self):
        if not self.counter:
            return None, 0
        return self.counter.most_common(1)[0]

    def top5(self):
        return self.counter.most_common(5)


def analyze(path):
    with open(path, newline="", encoding="utf-8") as f:
        columns = csv.DictReader(f).fieldnames

    types = infer_column_types(path, columns)

    accumulators = {}
    missing_counts = {c: 0 for c in columns}
    for c in columns:
        accumulators[c] = (
            NumericAccumulator() if types[c] in ("numeric", "range") else CategoricalAccumulator()
        )

    total_rows = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            for c in columns:
                val = row[c]
                if is_missing(val):
                    missing_counts[c] += 1
                    continue

                t = types[c]
                if t == "range":
                    parsed = try_parse_range_dict(val)
                    (accumulators[c].add(parsed) if parsed is not None else None)
                    if parsed is None:
                        missing_counts[c] += 1
                elif t == "numeric":
                    parsed = try_parse_number(val)
                    (accumulators[c].add(parsed) if parsed is not None else None)
                    if parsed is None:
                        missing_counts[c] += 1
                else:
                    accumulators[c].add(val.strip())

    print_report(columns, types, accumulators, missing_counts, total_rows)


def print_report(columns, types, accumulators, missing_counts, total_rows):
    print("=" * 80)
    print("PURE PYTHON DESCRIPTIVE STATISTICS REPORT")
    print("=" * 80)
    print(f"Total rows: {total_rows}")
    print(f"Total columns: {len(columns)}\n")

    for c in columns:
        acc = accumulators[c]
        t = types[c]
        print("-" * 80)
        print(f"Column: {c}  (inferred type: {t})")
        print(f"  Missing values: {missing_counts[c]} ({missing_counts[c] / total_rows:.1%})")

        if t in ("numeric", "range"):
            print(f"  Count:    {acc.count}")
            print(f"  Mean:     {acc.mean():.4f}" if acc.count else "  Mean: N/A")
            print(f"  Min:      {acc.min}")
            print(f"  Max:      {acc.max}")
            print(f"  Std Dev:  {acc.stdev():.4f}" if acc.count else "  Std Dev: N/A")
            print(f"  Median:   {acc.median()}")
            if t == "range":
                print("  Note: midpoint of lower/upper_bound range, or lower_bound alone if open-ended")
        else:
            print(f"  Count:    {acc.count}")
            print(f"  Unique:   {acc.nunique()}")
            mode_val, mode_freq = acc.mode()
            print(f"  Mode:     {mode_val!r} (freq={mode_freq})")
            print("  Top 5:")
            for val, freq in acc.top5():
                print(f"    {val!r}: {freq}")
        print()


if __name__ == "__main__":
    analyze(CSV_PATH)