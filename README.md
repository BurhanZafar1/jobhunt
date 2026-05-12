# Burhan's Job Hunt System

Automated discovery + scoring pipeline for 2026/2027 internships and 2027 full-time analyst roles. Targets finance, consulting, PE/REPE, strategy, BizOps, and FP&A across firms that match your experience profile.

## Build status

- [x] **Day 1 — Greenhouse + Lever scrapers → CSV** ← you are here
- [ ] Day 2 — Workday + Google Sheets dashboard
- [ ] Day 3 — Claude API scoring against your profile + rubric
- [ ] Day 4 — Daily email digest (top hits + deadlines)
- [ ] Day 5 — GitHub Actions cron deployment
- [ ] Day 6–7 — Tuning + adding firms based on actual results

## Setup (5 minutes, one time)

You need Python 3.10+. On Mac:

```bash
cd job-hunt-system
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows replace the third line with `.venv\Scripts\activate`.

## Run

```bash
python main.py
```

You'll see something like:

```
🔍 Job scraper run — 2026-05-12T14:30:00

Fetching 32 Greenhouse firms...
  ✓ Anthropic: 142 total
  ✓ Stripe: 89 total
  ✓ Airbnb: 54 total
  ✗ scaleai: 404 (slug wrong, fix in config.py)
  ...

Fetching 7 Lever firms...
  ✓ Netflix: 312 total
  ...

📊 Total jobs fetched: 1,247
📋 Relevant jobs after filtering: 34

✅ Written to: output/jobs_20260512_1430.csv
✅ Latest copy: output/jobs_latest.csv

Top 10 relevant jobs:
  • Stripe               | Strategy & Operations Analyst Intern, Summer 2027    | New York, NY
  • Anthropic            | Finance & Strategy Analyst                           | San Francisco
  ...
```

Open `output/jobs_latest.csv` in Excel or Google Sheets to review.

## How to add more firms

Edit `config.py`. Two lists:

```python
FIRMS_GREENHOUSE = [
    ("Display Name", "greenhouse-slug"),  # find slug in their careers page URL
    ...
]
FIRMS_LEVER = [
    ("Display Name", "lever-slug"),
    ...
]
```

To find a Greenhouse slug: go to the firm's careers page, look for `boards.greenhouse.io/SLUG` or `job-boards.greenhouse.io/SLUG` in the URL or page source.

For Lever: look for `jobs.lever.co/SLUG`.

If a slug 404s on first run, the script logs it. Fix or remove from the list.

## How to tune what's "relevant"

Edit `filters.py` (the keyword lists at the top of `config.py`):

- `RELEVANT_KEYWORDS` — title/description must contain at least one
- `EXCLUDE_KEYWORDS` — title containing any of these is dropped

After Day 3 ships, Claude API does the actual scoring and these keyword filters just do a first-pass culling.

## Troubleshooting

**Lots of "✗ 404" errors:** Greenhouse/Lever slugs change occasionally. Drop the offending firms from `config.py` and add replacements when you find them.

**Zero relevant jobs returned:** Filters might be too strict. Open `output/jobs_latest_raw.csv` (added in Day 2) to see what was fetched pre-filter.

**Script hangs:** Some firms have huge job boards (Amazon, Google). The async fetch has a 30-second timeout per firm; one slow firm won't block others.

## Cost

Day 1: **$0**. No API keys needed.

Day 3 adds Claude scoring at ~$0.50/day. Day 5 (GitHub Actions cron) is free.
