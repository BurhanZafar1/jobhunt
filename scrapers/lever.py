import asyncio, httpx
from scrapers.base import JobPosting
from config import LEVER_FIRMS

BASE = "https://api.lever.co/v0/postings/{slug}?mode=json&limit=500"

async def _fetch(client, firm):
    try:
        r = await client.get(BASE.format(slug=firm["slug"]), timeout=15)
        if r.status_code != 200:
            return firm["name"], []
        data = r.json()
        jobs = data if isinstance(data, list) else data.get("postings", [])
        postings = []
        for j in jobs:
            cats = j.get("categories", {})
            postings.append(JobPosting(
                company=firm["name"], title=j.get("text",""),
                location=cats.get("location","") or j.get("country",""),
                url=j.get("hostedUrl",""), description=j.get("descriptionPlain",""),
                source="lever", department=cats.get("team",""),
                posted_date=str(j.get("createdAt","")), job_id=j.get("id",""),
            ))
        return firm["name"], postings
    except Exception:
        return firm["name"], []

async def fetch_all_lever(verbose=True):
    all_jobs = []
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[_fetch(client, f) for f in LEVER_FIRMS])
    for name, jobs in results:
        if verbose:
            print(f"  {'✓' if jobs else '✗'} {len(jobs):>4} total                    {name}")
        all_jobs.extend(jobs)
    return all_jobs
