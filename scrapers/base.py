from dataclasses import dataclass, field

@dataclass
class JobPosting:
    company: str
    title: str
    location: str
    url: str
    description: str = ""
    source: str = ""
    department: str = ""
    posted_date: str = ""
    job_id: str = ""
    # Day 3 fields (Claude scoring)
    fit_score: float = 0.0
    category: str = ""
    why_it_fits: str = ""
    sponsors_intl: str = "Unknown"
    deadline: str = ""
