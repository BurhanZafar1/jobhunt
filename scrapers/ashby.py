"""
Ashby ATS scraper.
API: POST https://api.ashbyhq.com/posting-api/job-board/{slug}
Returns JSON with jobs[] array — no auth required.
"""

import asyncio
import httpx
from dataclasses import dataclass
from typing import Optional
from scrapers.base import JobPosting

ASHBY_FIRMS: list[dict] = [
    {"name": "OpenAI",       "slug": "openai"},
    {"name": "Anthropic",    "slug": "anthropic"},        # backup (also on GH)
    {"name": "Notion",       "slug": "notion"},
    {"name": "Linear",       "slug": "linear"},
    {"name": "Ramp",         "slug": "ramp"},
    {"name": "Plaid",        "slug": "plaid"},
    {"name": "Rippling",     "slug": "rippling"},
    {"name": "Retool",       "slug": "retool"},
    {"name": "Loom",         "slug": "loom"},
    {"name": "Lattice",      "slug": "lattice"},
    {"name": "Gem",          "slug": "gem"},
    {"name": "Watershed",    "slug": "watershed"},
    {"name": "Substack",     "slug": "substack"},
    {"name": "Replit",       "slug": "replit"},
    {"name": "Perplexity",   "slug": "perplexity-ai"},
    {"name": "Cohere",       "slug": "cohere"},
    {"name": "Scale AI",     "slug": "scale-ai"},
    {"name": "Ironclad",     "slug": "ironclad"},
    {"name": "Persona",      "slug": "persona"},
    {"name": "Ethena",       "slug": "ethena"},
]

ASHBY_BASE = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


async def _fetch_firm(client: httpx.AsyncClient, firm: dict) -> tuple[str, list[JobPosting]]:
    url = ASHBY_BASE.format(slug=firm["slug"])
    try:
        r = await client.post(url, json={}, timeout=15)
        if r.status_code != 200:
            return firm["name"], []
        data = r.json()
        jobs = data.get("jobPostings") or data.get("jobs") or []
        postings = []
        for j in jobs:
            # location
            loc_parts = []
            for loc in j.get("locationName", "").split(","):
                loc_parts.append(loc.strip())
            location = j.get("locationName") or "Unknown"

            posting = JobPosting(
                company=firm["name"],
                title=j.get("title", ""),
                location=location,
                url=j.get("jobUrl") or j.get("applyUrl") or "",
                description=j.get("descriptionSafe") or j.get("description") or "",
                source="ashby",
                department=j.get("department") or "",
                posted_date=j.get("publishedAt", ""),
                job_id=str(j.get("id", "")),
            )
            postings.append(posting)
        return firm["name"], postings
    except Exception:
        return firm["name"], []


async def fetch_all_ashby(verbose: bool = True) -> list[JobPosting]:
    all_jobs: list[JobPosting] = []
    async with httpx.AsyncClient() as client:
        tasks = [_fetch_firm(client, f) for f in ASHBY_FIRMS]
        results = await asyncio.gather(*tasks)

    for name, jobs in results:
        if verbose:
            if jobs:
                print(f"  ✓ {len(jobs):>4} total  (Ashby)  {name}")
            else:
                print(f"  ✗ 0 / 404  (Ashby)  {name}")
        all_jobs.extend(jobs)

    return all_jobs
