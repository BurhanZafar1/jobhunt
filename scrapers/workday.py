"""
Workday ATS scraper.
Each firm has its own subdomain: https://{tenant}.wd{n}.myworkdayjobs.com
Public API: GET /wday/cxs/{tenant}/{board}/jobs  (paginated, returns JSON)

Tested tenant IDs as of May 2026. Some may drift — if a firm 404s,
update WORKDAY_FIRMS with the correct tenant/board from the firm's career URL.
"""

import asyncio
import httpx
import re
from scrapers.base import JobPosting

WORKDAY_FIRMS: list[dict] = [
    # ── Bulge Bracket Banks ──────────────────────────────────────────────
    {
        "name": "Goldman Sachs",
        "url": "https://goldmansachs.wd1.myworkdayjobs.com/wday/cxs/goldmansachs/GS/jobs",
    },
    {
        "name": "JPMorgan Chase",
        "url": "https://jpmc.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
        "source_type": "oracle",  # JPM uses Oracle, not Workday — handled separately
    },
    {
        "name": "Morgan Stanley",
        "url": "https://ms.wd3.myworkdayjobs.com/wday/cxs/ms/Morgan_Stanley/jobs",
    },
    {
        "name": "Citigroup",
        "url": "https://citi.wd5.myworkdayjobs.com/wday/cxs/citi/FCB/jobs",
    },
    {
        "name": "Bank of America",
        "url": "https://bofa.wd1.myworkdayjobs.com/en-US/Global_Careers",
        "source_type": "bofa_custom",
    },
    {
        "name": "Barclays",
        "url": "https://barclays.wd3.myworkdayjobs.com/wday/cxs/barclays/Barclays_External/jobs",
    },
    {
        "name": "Deutsche Bank",
        "url": "https://db.wd3.myworkdayjobs.com/wday/cxs/db/DB_External_Career_Site/jobs",
    },
    {
        "name": "UBS",
        "url": "https://ubs.wd3.myworkdayjobs.com/wday/cxs/ubs/UBS/jobs",
    },
    {
        "name": "Wells Fargo",
        "url": "https://wellsfargo.wd5.myworkdayjobs.com/wday/cxs/wellsfargo/WellsFargoJobs/jobs",
    },
    # ── Elite Boutiques ───────────────────────────────────────────────────
    {
        "name": "Evercore",
        "url": "https://evercore.wd1.myworkdayjobs.com/wday/cxs/evercore/Evercore/jobs",
    },
    {
        "name": "Lazard",
        "url": "https://lazard.wd1.myworkdayjobs.com/wday/cxs/lazard/Lazard_External/jobs",
    },
    {
        "name": "Houlihan Lokey",
        "url": "https://hl.wd1.myworkdayjobs.com/wday/cxs/hl/HoulihanLokey/jobs",
    },
    {
        "name": "Jefferies",
        "url": "https://jefferies.wd1.myworkdayjobs.com/wday/cxs/jefferies/Jefferies/jobs",
    },
    {
        "name": "William Blair",
        "url": "https://williamblair.wd1.myworkdayjobs.com/wday/cxs/williamblair/WilliamBlair/jobs",
    },
    # ── MBB Consulting ────────────────────────────────────────────────────
    {
        "name": "McKinsey",
        "url": "https://mckinsey.wd12.myworkdayjobs.com/wday/cxs/mckinsey/MCKINSEY/jobs",
    },
    {
        "name": "BCG",
        "url": "https://bcg.wd3.myworkdayjobs.com/wday/cxs/bcg/BCG/jobs",
    },
    {
        "name": "Bain",
        "url": "https://bain.wd1.myworkdayjobs.com/wday/cxs/bain/Bain/jobs",
    },
    # ── T2 Consulting ─────────────────────────────────────────────────────
    {
        "name": "Deloitte",
        "url": "https://deloitte.wd1.myworkdayjobs.com/wday/cxs/deloitte/DeloitteUSA/jobs",
    },
    {
        "name": "Oliver Wyman",
        "url": "https://oliverwyman.wd5.myworkdayjobs.com/wday/cxs/oliverwyman/OliverWymanCareers/jobs",
    },
    {
        "name": "Kearney",
        "url": "https://kearney.wd1.myworkdayjobs.com/wday/cxs/kearney/Kearney/jobs",
    },
    # ── Private Equity / Real Estate PE ──────────────────────────────────
    {
        "name": "Blackstone",
        "url": "https://blackstone.wd1.myworkdayjobs.com/wday/cxs/blackstone/Blackstone/jobs",
    },
    {
        "name": "KKR",
        "url": "https://kkr.wd1.myworkdayjobs.com/wday/cxs/kkr/KKR/jobs",
    },
    {
        "name": "Carlyle",
        "url": "https://carlyle.wd1.myworkdayjobs.com/wday/cxs/carlyle/Carlyle/jobs",
    },
    {
        "name": "Apollo",
        "url": "https://apollo.wd5.myworkdayjobs.com/wday/cxs/apollo/Apollo/jobs",
    },
    {
        "name": "Brookfield",
        "url": "https://brookfield.wd3.myworkdayjobs.com/wday/cxs/brookfield/Brookfield/jobs",
    },
    {
        "name": "Ares Management",
        "url": "https://ares.wd1.myworkdayjobs.com/wday/cxs/ares/Ares/jobs",
    },
    # ── Asset Management ─────────────────────────────────────────────────
    {
        "name": "BlackRock",
        "url": "https://blackrock.wd1.myworkdayjobs.com/wday/cxs/blackrock/BlackRock/jobs",
    },
    {
        "name": "Fidelity",
        "url": "https://fidelity.wd5.myworkdayjobs.com/wday/cxs/fidelity/Enterprise/jobs",
    },
    {
        "name": "Vanguard",
        "url": "https://vanguard.wd5.myworkdayjobs.com/wday/cxs/vanguard/Vanguard/jobs",
    },
    {
        "name": "T. Rowe Price",
        "url": "https://troweprice.wd5.myworkdayjobs.com/wday/cxs/troweprice/TRowePrice/jobs",
    },
]

WORKDAY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

PAGE_SIZE = 20  # Workday default; bump to 50 if you want fewer pages


def _parse_workday_job(j: dict, company: str, base_apply_url: str) -> JobPosting:
    """Normalize a single Workday job dict."""
    # Location
    locations = j.get("locationsText", "") or ""
    if not locations:
        locs = j.get("locations") or []
        locations = ", ".join(
            loc.get("descriptor", "") for loc in locs if loc.get("descriptor")
        ) or "Unknown"

    # Apply URL
    ext_id = j.get("externalPath") or j.get("id") or ""
    apply_url = f"{base_apply_url.rstrip('/')}{ext_id}" if ext_id else base_apply_url

    # Posted date
    posted = j.get("postedOn") or j.get("startDate") or ""

    return JobPosting(
        company=company,
        title=j.get("title", {}).get("descriptor", "") if isinstance(j.get("title"), dict) else j.get("title", ""),
        location=locations,
        url=apply_url,
        description=j.get("jobDescription", {}).get("descriptor", "") if isinstance(j.get("jobDescription"), dict) else "",
        source="workday",
        department=j.get("jobFunction", {}).get("descriptor", "") if isinstance(j.get("jobFunction"), dict) else "",
        posted_date=posted,
        job_id=str(j.get("id") or j.get("bulletFields", [""])[0] or ""),
    )


async def _fetch_workday_firm(
    client: httpx.AsyncClient, firm: dict
) -> tuple[str, list[JobPosting]]:
    """Paginate through all jobs for one Workday firm."""
    if firm.get("source_type") in ("oracle", "bofa_custom"):
        # Skip non-Workday entries for now; Week 3 will handle them
        return firm["name"], []

    base_url = firm["url"]
    # Derive the human-facing career URL for apply links
    # e.g. https://goldmansachs.wd1.myworkdayjobs.com/GS
    apply_base = re.sub(r"/wday/cxs/[^/]+/[^/]+/jobs.*", "", base_url)

    all_jobs: list[JobPosting] = []
    offset = 0

    try:
        while True:
            payload = {"limit": PAGE_SIZE, "offset": offset}
            r = await client.post(base_url, json=payload, headers=WORKDAY_HEADERS, timeout=20)
            if r.status_code != 200:
                break
            data = r.json()
            jobs_page = data.get("jobPostings") or data.get("jobs") or []
            if not jobs_page:
                break
            for j in jobs_page:
                all_jobs.append(_parse_workday_job(j, firm["name"], apply_base))
            # Stop if we got fewer than page size (last page)
            if len(jobs_page) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
            # Safety cap — no firm has >1000 postings we care about
            if offset > 1000:
                break
    except Exception:
        pass

    return firm["name"], all_jobs


async def fetch_all_workday(verbose: bool = True) -> list[JobPosting]:
    all_jobs: list[JobPosting] = []
    async with httpx.AsyncClient() as client:
        tasks = [_fetch_workday_firm(client, f) for f in WORKDAY_FIRMS]
        results = await asyncio.gather(*tasks)

    for name, jobs in results:
        if verbose:
            if jobs:
                print(f"  ✓ {len(jobs):>4} total  (Workday) {name}")
            else:
                print(f"  ✗ 0 / err  (Workday) {name}")
        all_jobs.extend(jobs)

    return all_jobs
