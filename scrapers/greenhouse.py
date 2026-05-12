import asyncio, httpx
from scrapers.base import JobPosting
from config import GREENHOUSE_FIRMS

BASE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"

async def _fetch(client, firm):
    try:
        r = await client.get(BASE.format(slug=firm["slug"]), timeout=15)
        if r.status_code != 200:
            return firm["name"], []
        jobs = r.json().get("jobs", [])
        postings = []
        for j in jobs:
            postings.append(JobPosting(
                company=firm["name"], title=j.get("title",""),
                location=j.get("location",{}).get("name","") if isinstance(j.get("location"),dict) else str(j.get("location","")),
                url=j.get("absolute_url",""), description=j.get("content",""),
                source="greenhouse", department=j.get("departments",[{}])[0].get("name","") if j.get("departments") else "",
                posted_date=j.get("updated_at",""), job_id=str(j.get("id","")),
            ))
        return firm["name"], postings
    except Exception:
        return firm["name"], []

async def fetch_all_greenhouse(verbose=True):
    all_jobs = []
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[_fetch(client, f) for f in GREENHOUSE_FIRMS])
    for name, jobs in results:
        if verbose:
            print(f"  {'✓' if jobs else '✗'} {len(jobs):>4} total                    {name}")
        all_jobs.extend(jobs)
    return all_jobs
