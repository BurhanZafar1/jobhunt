import asyncio, csv, json, os, re, time
from pathlib import Path
import httpx

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 10
CSV_PATH = Path("output/jobs_latest.csv")

CANDIDATE_SUMMARY = (
    "Burhan | Whitman College, Economics & Math, GPA 3.76, graduating May 2027. "
    "Visa: F-1 (needs OPT/CPT for internships, sponsorship for FT). "
    "Experiences: Real Estate PE Project Destined top 4.5%, Investment Research Whitman Investment Co, "
    "Goldman Sachs 250M endowment project, FP&A at Al Noor Sugar Python/Excel automation, "
    "Tableau Power BI analytics, AI full-stack React FastAPI AWS Claude API. "
    "Target roles: IB SA/Analyst, REPE, Equity Research, MBB Consulting, FP&A/Corp Finance, Strategy & Ops."
)

SCORE_PROMPT = (
    "Score this job for the candidate. Respond ONLY in valid JSON, no other text.\n\n"
    "CANDIDATE: {candidate}\n\n"
    "JOB:\nCompany: {company}\nTitle: {title}\nLocation: {location}\n"
    "Department: {department}\nDescription: {description}\n\n"
    'Respond with exactly this JSON:\n'
    '{{"fit_score": <1-10>, '
    '"category": "<Investment Banking|Private Equity / Venture|Real Estate PE|Equity Research / HF|Asset Management|Sales & Trading|Management Consulting|Corp Dev / M&A|FP&A / Finance|Strategy & Ops / BizOps|Data / Analytics|Rotational|Skip>", '
    '"why_it_fits": "<one sentence>", '
    '"sponsors_intl": "<Yes|No|Unknown>", '
    '"timing": "<Summer 2026|Summer 2027|Full-Time 2027|Other|Unknown>"}}\n\n'
    "RUBRIC: 9-10=direct match IB SA REPE MBB, 7-8=strong match FP&A corp strategy asset mgmt, "
    "5-6=adjacent fintech strategy bizops, 3-4=stretch, 1-2=wrong level or visa blocked. "
    "Score 1-2 for: engineering, sales SDR, marketing, HR, customer success, director VP, citizenship required."
)

async def score_job(client, job):
    prompt = SCORE_PROMPT.format(
        candidate=CANDIDATE_SUMMARY,
        company=job.get("company", ""),
        title=job.get("title", ""),
        location=job.get("location", ""),
        department=job.get("department", ""),
        description=(job.get("description", "") or "")[:600],
    )
    try:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={"model": MODEL, "max_tokens": 250, "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        text = r.json()["content"][0]["text"].strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        parsed = json.loads(text)
        job["fit_score"]     = int(parsed.get("fit_score", 0))
        job["category"]      = parsed.get("category", job.get("category", ""))
        job["why_it_fits"]   = parsed.get("why_it_fits", "")
        job["sponsors_intl"] = parsed.get("sponsors_intl", "Unknown")
        job["timing"]        = parsed.get("timing", "Unknown")
    except Exception as e:
        job["fit_score"] = 0
        job["why_it_fits"] = "Error: " + str(e)
        job["sponsors_intl"] = "Unknown"
        job["timing"] = "Unknown"
    return job

async def score_all(jobs):
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("Run: export ANTHROPIC_API_KEY='sk-ant-...'")
        return jobs
    scored = []
    async with httpx.AsyncClient() as client:
        for i in range(0, len(jobs), BATCH_SIZE):
            batch = jobs[i:i + BATCH_SIZE]
            results = await asyncio.gather(*[score_job(client, j) for j in batch])
            scored.extend(results)
            done = min(i + BATCH_SIZE, len(jobs))
            scores = [j["fit_score"] for j in results if j.get("fit_score")]
            avg = sum(scores) / len(scores) if scores else 0
            print(f"  Scored {done:>3}/{len(jobs)}  avg: {avg:.1f}")
            if i + BATCH_SIZE < len(jobs):
                await asyncio.sleep(0.5)
    return scored

def push_to_sheets(jobs, sheet_id):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_file(
            "service_account.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc = gspread.authorize(creds)
        ss = gc.open_by_key(sheet_id)
    except Exception as e:
        print(f"Sheets error: {e}")
        return

    headers = ["Fit Score", "Company", "Role Title", "Category", "Timing",
               "Location", "Source", "Sponsors Intl?", "Why It Fits", "Apply URL"]

    def row(j):
        return [
            j.get("fit_score", ""), j.get("company", ""), j.get("title", ""),
            j.get("category", ""), j.get("timing", ""), j.get("location", ""),
            j.get("source", ""), j.get("sponsors_intl", ""),
            j.get("why_it_fits", ""), j.get("url", ""),
        ]

    sorted_jobs = sorted(jobs, key=lambda j: j.get("fit_score", 0), reverse=True)

    try:
        ws = ss.worksheet("Today's New Postings")
    except Exception:
        ws = ss.add_worksheet("Today's New Postings", 1000, len(headers))
    ws.clear()
    ws.append_row(headers)
    if sorted_jobs:
        ws.append_rows([row(j) for j in sorted_jobs])
    print(f"  Today's New Postings: {len(sorted_jobs)} rows")

    try:
        ws2 = ss.worksheet("Apply This Week")
    except Exception:
        ws2 = ss.add_worksheet("Apply This Week", 500, len(headers))
        ws2.append_row(headers)
    existing = ws2.get_all_values()
    existing_urls = {r[9] for r in existing[1:] if len(r) > 9}
    new_high = [j for j in sorted_jobs
                if j.get("fit_score", 0) >= 7 and j.get("url", "") not in existing_urls]
    if new_high:
        ws2.append_rows([row(j) for j in new_high])
    print(f"  Apply This Week: {len(new_high)} new high-fit jobs (7+)")
    print(f"  https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

async def main():
    print("\n--- Claude Scorer Day 3 ---")
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found. Run main.py first.")
        return
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        jobs = list(csv.DictReader(f))
    print(f"Loaded {len(jobs)} jobs from CSV")
    print(f"Scoring with {MODEL} in batches of {BATCH_SIZE}...\n")
    start = time.time()
    scored = await score_all(jobs)
    elapsed = time.time() - start
    print(f"\nCompleted in {elapsed:.0f}s")
    high = [j for j in scored if j.get("fit_score", 0) >= 7]
    mid  = [j for j in scored if 5 <= j.get("fit_score", 0) < 7]
    print(f"  {len(high)} high fit (7+) -> Apply This Week")
    print(f"  {len(mid)} mid fit (5-6) -> worth reviewing")
    top = sorted(scored, key=lambda j: j.get("fit_score", 0), reverse=True)[:10]
    print("\nTop 10:")
    for j in top:
        print(f"  {j.get('fit_score',0)}  {j.get('company','')[:22]:<22}  {j.get('title','')[:40]}")
    Path("output").mkdir(exist_ok=True)
    with open("output/jobs_scored.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(scored[0].keys()), extrasaction="ignore")
        w.writeheader()
        w.writerows(scored)
    print("\nSaved: output/jobs_scored.csv")
    from config import GOOGLE_SHEET_ID
    if GOOGLE_SHEET_ID and "PASTE" not in GOOGLE_SHEET_ID:
        push_to_sheets(scored, GOOGLE_SHEET_ID)

if __name__ == "__main__":
    asyncio.run(main())
