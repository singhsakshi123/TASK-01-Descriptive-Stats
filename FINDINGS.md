# Findings: 2024 Facebook Presidential Ad Spending

Political advertising on Facebook during the 2024 election was heavily
concentrated rather than evenly distributed. Across 246,745 ad purchases from
4,546 distinct pages, the top 10 spending pages accounted for roughly **63%**
of total estimated spend (~$262M in midpoint-estimated spend overall).
Kamala Harris's own page was the largest single spender, also the single
most frequent page in the dataset by ad count (55,503 ads — over twice
Donald J. Trump's official page at 23,988). This concentration shows up
consistently: the top 5 pages by ad volume (Kamala Harris, Donald J. Trump,
Joe Biden, The Daily Scroll, Kamala HQ) together account for a large share
of all activity in a dataset of 4,546 pages.

Estimated audience size is itself skewed toward the largest bucket: **100,146
ads (~41% of all ads)** were targeted at audiences Meta only reports as
"1,000,001+" — an open-ended range with no upper bound. That single bucket
being the mode of the column is a useful signal on its own: a large share of
2024 election ad spend was aimed at the broadest possible audience tier
Meta allows advertisers to report, rather than narrowly targeted segments.
Median estimated audience size across all ads was 300,000.

Spending was also sharply concentrated in time. Monthly spend was negligible
through 2023, began accelerating in mid-2024, and spiked dramatically in the
final stretch of the race: spend roughly tripled from September ($45M) to
October 2024 ($85M) — the month immediately before the election — consistent
with a "closing argument" surge in campaign advertising.

On mentions, Donald Trump was named in far more ads (78,324 combining
"Donald Trump" and "President Trump" mentions) than any other figure,
followed by Kamala Harris (53,239 combined) and Joe Biden (24,247, reflecting
mentions before he dropped out). 73,205 ads (about 30%) mention no tracked
candidate at all. This is a useful contrast with the spend numbers: Trump is
mentioned most often, but Kamala Harris's own page spent and posted the
most — suggesting mention volume and spend volume are driven by different
dynamics (one reflects being the subject of ads run by many pages, including
attack ads from opponents, the other reflects a campaign's own paid
promotion).

Data quality: most columns are complete. The main gaps are
`estimated_audience_size` (missing for 0.23% of rows — smaller than initially
appeared, since most "missing-looking" values were actually valid open-ended
ranges that just needed correct parsing), and small pockets of missing
`ad_delivery_stop_time` (0.87%) and `bylines` (0.41%).

What surprised me: 
What surprised me most wasn't a number — it was how much a single line of
parsing logic could hide an entire pattern in the data. When I first ran
estimated_audience_size, it silently fell into the categorical bucket
because my range parser only handled rows with both a lower_bound and an
upper_bound. It wasn't until I looked closer that I realized 41% of all
246,745 ads — the single largest chunk of the dataset — were targeted at
audiences Meta only reports as "1,000,001+," an open-ended range with
no ceiling at all. That's not a data quality issue to shrug off; it means
close to half of the ads in this dataset were aimed at the broadest
possible audience tier advertisers are even allowed to report, and I
would have completely missed that if Pandas' describe() had just quietly
worked on the first try.

I was also struck by how lopsided the "who's spending" story is compared
to the "who's mentioned" story. Kamala Harris's own page was both the
single most active advertiser (55,503 ads) and among the top spenders,
while Donald Trump was mentioned in more ads overall than any other
figure — but a lot of those mentions came from other pages running attack
ads against him, not from his own campaign spend. Spend and mentions
are answering two different questions, and it hadn't occurred to me
before this task that "how often is a candidate talked about" and "how
much money is behind that candidate" could point in almost opposite
directions.

Finally, the fact that 30% of ads (73,205 of them) don't mention any
tracked candidate at all was unexpected. It's a reminder that a lot of
what counts as "political advertising" in this dataset is happening
around the edges of the named candidates — fundraising asks, get-out-
the-vote messaging, issue ads — rather than being centered on attacking
or promoting a specific person.