# Comparison: Pure Python vs. Pandas

**Do the results agree?**
Yes — after fixing a parsing bug (see below), numeric columns match exactly
to the reported decimal precision. `spend` mean: 1061.7914 vs 1061.791434.
`impressions` mean: 45602.0214 vs 45602.021360. Both scripts use the same
sample stdev convention (n-1 denominator, pandas' default) and the same
range-midpoint treatment, so there was nothing left to reconcile once the
parsing logic matched.

**A real bug the manual version caught that Pandas would have hidden:**
`estimated_audience_size` values aren't always a `{lower_bound, upper_bound}`
pair — some rows only report `lower_bound` (an open-ended range, e.g.
"1,000,001+", covering 41% of all rows). My first version of the midpoint
parser required both keys and silently failed on the open-ended rows,
which caused the *entire column* to get classified as categorical instead
of numeric in pure Python. Writing the type-inference logic by hand forced
me to notice this; pandas' `read_csv` would have just left the column as an
`object` dtype without ever surfacing that some values had a different shape
than others. This was the single most useful discovery of the assignment —
a case where "no crash" (pandas silently keeps going) is actually worse
than an obvious failure (my script's stats output made the missing case
impossible to miss).

**A real discrepancy the two scripts still don't agree on:**
`bylines` unique-value count: pure Python reports 3,786 unique values,
pandas reports 3,790. The pure-Python script calls `.strip()` on every
categorical value before counting it; `pd.read_csv` does not strip
whitespace by default. So a handful of byline values with stray leading or
trailing spaces are treated as distinct strings by pandas but collapsed
into one value by the manual script. Neither answer is "more correct" —
it's a reminder that "how many unique values" is not a neutral question;
it depends on a normalization decision that's easy to make invisibly.

**Structural difference (not a data disagreement):**
The pandas script ends up with 43 columns vs. pure Python's 40, because it
adds `_mid` columns alongside the original range-dict columns instead of
overwriting them. That means pandas' categorical summary still lists
`spend`, `impressions`, and `estimated_audience_size` as object columns
(with their raw dict-string value counts) *in addition to* the numeric
`_mid` versions. This was a deliberate choice to keep the transformation
auditable, not something forced by the library.

**What the manual version taught me that Pandas would have hidden:**
Writing `mean()`/type inference by hand forces a decision about every
malformed or oddly-shaped value individually. `df.describe()` and
`read_csv`'s dtype inference just work — convenient, but they can run
successfully on a column whose actual structure (like the two different
shapes of `estimated_audience_size`) you don't fully understand yet.
