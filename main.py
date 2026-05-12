"""
Job Hunt Automation — Day 2
Runs: Greenhouse + Lever (Day 1) + Ashby + Workday (Day 2)
Pushes results to Google Sheets dashboard.
"""

import asyncio
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from config import CANDIDATE_PROFILE, GOOGLE_SHEET_ID
from filters import filter_jobs, deduplicate, CATEGORY_PRIORITY
from scrapers.greenhouse import fetch_all_greenhouse
from scrapers.lever import fetch_all_lever
from scrapers.ashby import fetch_all_ashby
from scrapers.workday import fetch_all_workday
from sheets import push_to_sheets


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


async def main():
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    print(f"\n🔍 Job scraper run — {datetime.now().isoformat(timespec='seconds')}\n")

    # ── 1. Scrape all sources in parallel ────────────────────────────────
    print("── Greenhouse ─────────────────────────────────────────────────")
    gh_jobs = await fetch_all_greenhouse(verbose=True)

    print("\n── Lever ───────────────────────────────────────────────────────")
    lv_jobs = await fetch_all_lever(verbose=True)

    print("\n── Ashby ───────────────────────────────────────────────────────")
    ab_jobs = await fetch_all_ashby(verbose=True)

    print("\n── Workday ─────────────────────────────────────────────────────")
    wd_jobs = await fetch_all_workday(verbose=True)

    all_jobs = gh_jobs + lv_jobs + ab_jobs + wd_jobs
    print(f"\n📥 Total fetched: {len(all_jobs)} jobs across all sources")

    # ── 2. Filter + dedup ────────────────────────────────────────────────
    relevant = filter_jobs(all_jobs)
    relevant = deduplicate(relevant)

    print(f"✅ Relevant after filter/dedup: {len(relevant)} jobs\n")

    # Category breakdown
    from collections import Counter
    cat_counts = Counter(getattr(j, "category", "?") for j in relevant)
    print("By category:")
    for cat in CATEGORY_PRIORITY:
        c = cat_counts.get(cat, 0)
        if c:
            print(f"  {c:>4}  {cat}")
    other = sum(v for k, v in cat_counts.items() if k not in CATEGORY_PRIORITY)
    if other:
        print(f"  {other:>4}  Other")

    # ── 3. Write CSV ─────────────────────────────────────────────────────
    csv_path = OUTPUT_DIR / "jobs_latest.csv"
    ts_path  = OUTPUT_DIR / f"jobs_{ts}.csv"
    raw_path = OUTPUT_DIR / f"jobs_raw_{ts}.csv"

    fieldnames = [
        "company", "title", "category", "location", "source",
        "posted_date", "url", "department", "job_id"
    ]

    for path, data in [(csv_path, relevant), (ts_path, relevant), (raw_path, all_jobs)]:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for j in data:
                writer.writerow({
                    "company": j.company,
                    "title": j.title,
                    "category": getattr(j, "category", ""),
                    "location": j.location,
                    "source": j.source,
                    "posted_date": j.posted_date,
                    "url": j.url,
                    "department": j.department,
                    "job_id": j.job_id,
                })

    print(f"\n💾 Saved: {csv_path}")

    # ── 4. Preview top 20 ────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print(f"{'CATEGORY':<22} {'COMPANY':<20} {'TITLE':<40}")
    print("─" * 72)
    for j in relevant[:40]:
        cat = getattr(j, "category", "")[:21]
        co  = j.company[:19]
        ttl = j.title[:39]
        print(f"{cat:<22} {co:<20} {ttl:<40}")
    if len(relevant) > 40:
        print(f"  … and {len(relevant)-40} more in the CSV")
    print("─" * 72)

    # ── 5. Push to Google Sheets ─────────────────────────────────────────
    print()
    push_to_sheets(
        relevant,
        sheet_id=GOOGLE_SHEET_ID,
        verbose=True,
    )

    print("\n✅ Done. Open output/jobs_latest.csv or your Google Sheet.\n")


if __name__ == "__main__":
    asyncio.run(main())
