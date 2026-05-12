"""
filters.py — v1.2
- Title-only keyword matching (no false triggers from description text)
- Location-field-only US check
- Word-boundary regex for exclude patterns
- Deduplication by (company, normalized title, location)
- Category assignment + priority sort
"""

import re
from scrapers.base import JobPosting
from config import (
    REQUIRED_TITLE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_LOCATIONS,
    CATEGORY_KEYWORDS,
)

CATEGORY_PRIORITY = [
    "Investment Banking",
    "Private Equity / Venture",
    "Real Estate PE",
    "Equity Research / HF",
    "Asset Management",
    "Sales & Trading",
    "Management Consulting",
    "Corp Dev / M&A",
    "FP&A / Finance",
    "Strategy & Ops / BizOps",
    "Data / Analytics",
    "Rotational",
]

_EXCLUDE_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in EXCLUDE_TITLE_KEYWORDS]
_REQUIRED_PATTERN = re.compile(
    r"(?i)\b(" + "|".join(re.escape(k) for k in REQUIRED_TITLE_KEYWORDS) + r")\b"
)


def _is_us_location(location: str) -> bool:
    """Return True if the location field looks US-based."""
    if not location or location.strip().lower() in ("remote", "unknown", ""):
        return True   # keep if location is ambiguous
    loc_lower = location.lower()
    # Explicit non-US signal — drop
    for excl in EXCLUDE_LOCATIONS:
        if excl in loc_lower:
            return False
    return True


def _assign_category(job: JobPosting) -> str:
    text = (job.title + " " + job.department).lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                return cat
    # Fallback based on broad title signals
    title_l = job.title.lower()
    if any(w in title_l for w in ["analyst", "associate"]):
        return "FP&A / Finance"
    if "data" in title_l:
        return "Data / Analytics"
    if "strategy" in title_l or "operations" in title_l:
        return "Strategy & Ops / BizOps"
    return "Finance (general)"


def _passes_title_filter(title: str) -> bool:
    title_l = title.lower()
    # Must have at least one required keyword
    if not _REQUIRED_PATTERN.search(title):
        return False
    # Must not have any exclude keyword
    for pat in _EXCLUDE_PATTERNS:
        if pat.search(title):
            return False
    return True


def filter_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    kept = []
    for j in jobs:
        if not j.title:
            continue
        if not _passes_title_filter(j.title):
            continue
        if not _is_us_location(j.location):
            continue
        j.category = _assign_category(j)
        kept.append(j)

    # Sort by category priority, then company
    def sort_key(j):
        try:
            rank = CATEGORY_PRIORITY.index(j.category)
        except ValueError:
            rank = len(CATEGORY_PRIORITY)
        return (rank, j.company.lower())

    kept.sort(key=sort_key)
    return kept


def deduplicate(jobs: list[JobPosting]) -> list[JobPosting]:
    """Collapse same role posted across multiple office locations."""
    seen: dict[tuple, JobPosting] = {}
    for j in jobs:
        # Normalize title for dedup key
        norm_title = re.sub(r"\s+", " ", j.title.lower().strip())
        norm_title = re.sub(r"[^\w\s]", "", norm_title)
        key = (j.company.lower(), norm_title)

        if key not in seen:
            seen[key] = j
        else:
            # Merge locations
            existing_locs = seen[key].location.split(" / ")
            new_loc = j.location.strip()
            if new_loc and new_loc not in existing_locs:
                existing_locs.append(new_loc)
                seen[key].location = " / ".join(existing_locs)

    return list(seen.values())
