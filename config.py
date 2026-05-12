"""
config.py — v2.0
Day 2: added Ashby + Workday firms, Google Sheet ID field.
"""

# ──────────────────────────────────────────────────────────────────────────────
# GOOGLE SHEETS — paste your Sheet ID here after setup
# (the long string in your sheet URL between /d/ and /edit)
# ──────────────────────────────────────────────────────────────────────────────
GOOGLE_SHEET_ID = "1wNPUZKmbk5opgs1EdzgmqQPBmzsRAeUdEoEVFiOa8Sk"

# ──────────────────────────────────────────────────────────────────────────────
# CANDIDATE PROFILE  (used by Day 3 Claude scoring prompt)
# ──────────────────────────────────────────────────────────────────────────────
CANDIDATE_PROFILE = {
    "name": "Burhan",
    "school": "Whitman College",
    "major": "Economics & Mathematics",
    "gpa": 3.76,
    "grad_year": 2027,
    "visa": "F-1 (needs OPT/CPT for internships, sponsorship for FT)",
    "experiences": [
        "Real Estate Private Equity — Project Destined (top 4.5% of 2,000+); underwrote live multifamily deal, DCF, 15-20% IRR",
        "Investment research — Whitman Investment Company; 5+ memos, TAM/SAM/SOM, comps",
        "Goldman Sachs Strategic Endowment Asset Allocation Project ($250M cross-asset, 17-slide IC deck)",
        "FP&A — Al Noor Sugar; Python/Excel automation, variance reporting, cost-center analysis",
        "Data analytics / BI — Gesa Power House Theatre; Tableau, Power BI, fuzzy-match CRM tool (92% accuracy, 20K records)",
        "AI/full-stack — AI cost-routing engine, AI grading tool, automated outreach pipeline (React, FastAPI, Claude API, AWS)",
    ],
    "target_roles": [
        "Investment Banking Summer Analyst / Full-Time Analyst",
        "Private Equity / Real Estate PE Intern or Analyst",
        "Equity Research / Hedge Fund / Asset Management",
        "Management Consulting (MBB / T2 / strategy boutique)",
        "Corporate Finance Rotational / FP&A / Treasury",
        "Data Analytics / Strategy & Operations / BizOps",
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# GREENHOUSE FIRMS  (slug = the identifier in their API URL)
# ──────────────────────────────────────────────────────────────────────────────
GREENHOUSE_FIRMS: list[dict] = [
    {"name": "Stripe",         "slug": "stripe"},
    {"name": "Brex",           "slug": "brex"},
    {"name": "Chime",          "slug": "chime"},
    {"name": "Robinhood",      "slug": "robinhood"},
    {"name": "Affirm",         "slug": "affirm"},
    {"name": "Coinbase",       "slug": "coinbase"},
    {"name": "Figma",          "slug": "figma"},
    {"name": "Databricks",     "slug": "databricks"},
    {"name": "Snowflake",      "slug": "snowflake"},
    {"name": "Cloudflare",     "slug": "cloudflare"},
    {"name": "Datadog",        "slug": "datadog"},
    {"name": "HubSpot",        "slug": "hubspot"},
    {"name": "MongoDB",        "slug": "mongodb"},
    {"name": "Pinterest",      "slug": "pinterest"},
    {"name": "Lyft",           "slug": "lyft"},
    {"name": "DraftKings",     "slug": "draftkings"},
    {"name": "Block",          "slug": "block"},
    {"name": "Twilio",         "slug": "twilio"},
    {"name": "Asana",          "slug": "asana"},
    {"name": "Benchling",      "slug": "benchling"},
    {"name": "Navan",          "slug": "tripactions"},
    {"name": "Relativity",     "slug": "relativity"},
    {"name": "Marqeta",        "slug": "marqeta"},
    {"name": "Samsara",        "slug": "samsara"},
    {"name": "Gusto",          "slug": "gusto"},
    {"name": "Zendesk",        "slug": "zendesk"},
    {"name": "Squarespace",    "slug": "squarespace"},
    {"name": "Webflow",        "slug": "webflow"},
    {"name": "Carta",          "slug": "carta"},
    {"name": "Strava",         "slug": "strava"},
]

# ──────────────────────────────────────────────────────────────────────────────
# LEVER FIRMS
# ──────────────────────────────────────────────────────────────────────────────
LEVER_FIRMS: list[dict] = [
    {"name": "Airbnb",         "slug": "airbnb"},
    {"name": "Spotify",        "slug": "spotify"},
    {"name": "Reddit",         "slug": "reddit"},
    {"name": "Duolingo",       "slug": "duolingo"},
    {"name": "Canva",          "slug": "canva"},
]

# ──────────────────────────────────────────────────────────────────────────────
# TITLE FILTERS
# ──────────────────────────────────────────────────────────────────────────────

# A job must match at least ONE of these in the title to be considered relevant.
REQUIRED_TITLE_KEYWORDS: list[str] = [
    "analyst", "associate", "intern", "internship",
    "finance", "financial", "investment", "banking",
    "consulting", "consultant", "strategy", "strategic",
    "operations", "operator", "treasury", "fp&a",
    "equity", "capital", "asset", "portfolio",
    "business development", "corporate development",
    "rotational", "rotation",
    "data", "research", "economics", "quant",
    "risk", "compliance",
]

# Reject if ANY of these appear in the title (whole-word matching where marked \b).
EXCLUDE_TITLE_KEYWORDS: list[str] = [
    # Engineering
    r"\bengineer\b", r"\bdeveloper\b", r"\bprogrammer\b",
    r"\bdevops\b", r"\bsre\b", r"\binfrastructure\b",
    r"\bbackend\b", r"\bfrontend\b", r"\bfullstack\b",
    r"\bmachine learning\b", r"\bml engineer\b", r"\bai engineer\b",
    r"\bsoftware\b", r"\bplatform\b", r"\bcloud\b",
    # Design / Product
    r"\bdesign\b", r"\bdesigner\b", r"\bux\b", r"\bui\b",
    r"\bproduct manager\b", r"\bpm\b",
    # Marketing / Sales / Support
    r"\bmarketing\b", r"\bgrowth\b", r"\bseo\b", r"\bcontent\b",
    r"\bsocial media\b", r"\bbrand\b", r"\bcommunications\b",
    r"\bpublic relations\b", r"\bpr\b",
    r"\bsales development\b", r"\bsdr\b", r"\bbdr\b",
    r"\baccount executive\b", r"\baccount manager\b",
    r"\bcustomer success\b", r"\bcustomer support\b",
    r"\bcustomer operations\b", r"\bcustomer experience\b",
    r"\bvalue consultant\b", r"\bfield consultant\b",
    r"\bsolutions consultant\b", r"\bpre.?sales\b",
    # HR / Recruiting
    r"\brecruiting\b", r"\brecruiter\b", r"\btalent\b",
    r"\bhuman resources\b", r"\bhr\b",
    # Senior levels
    r"\bsenior\b", r"\bstaff\b", r"\bprincipal\b",
    r"\bvp\b", r"\bvice president\b", r"\bdirector\b",
    r"\bmanaging director\b", r"\bmd\b", r"\bpartner\b",
    r"\bcto\b", r"\bcfo\b", r"\bcoo\b", r"\bceo\b",
    r"\blead\b",   # catches Lead, Lead,  — word boundary handles suffixes
    r"\bmanager\b",
    # Compliance / Legal (usually needs law degree)
    r"\blegal\b", r"\bcounsel\b", r"\bparalegal\b",
    r"\bcompliance officer\b",
    # Misc non-targets
    r"\bphysician\b", r"\bnurse\b", r"\bclinical\b",
    r"\bteacher\b", r"\btutor\b",
    r"\breal estate agent\b", r"\bleasing\b", r"\bproperty manager\b",
]

# If location field contains these, drop the job.
EXCLUDE_LOCATIONS: list[str] = [
    "london", "paris", "berlin", "tokyo", "singapore", "sydney",
    "toronto", "montreal", "vancouver", "bangalore", "hyderabad",
    "mumbai", "delhi", "mexico", "são paulo", "sao paulo", "bogota",
    "amsterdam", "dublin", "zurich", "hong kong", "dubai",
    "uk", "u.k.", "united kingdom", "india", "canada", "australia",
    "germany", "france", "spain", "italy", "netherlands",
    "remote - international", "apac", "emea", "latam",
]

# ──────────────────────────────────────────────────────────────────────────────
# CATEGORY MAP — used to assign display labels
# ──────────────────────────────────────────────────────────────────────────────
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Investment Banking": [
        "investment bank", "ib", "capital markets", "m&a",
        "mergers", "acquisitions", "leveraged finance",
        "restructuring", "dcm", "ecm", "syndicate",
    ],
    "Private Equity / Venture": [
        "private equity", " pe ", "venture capital", "vc ",
        "growth equity", "buyout", "lbo",
    ],
    "Real Estate PE": [
        "real estate", "repe", "reit", "property", "cre",
        "commercial real estate",
    ],
    "Equity Research / HF": [
        "equity research", "hedge fund", "long/short",
        "buy-side", "buyside", "investment research",
        "stock pitch", "portfolio management",
    ],
    "Asset Management": [
        "asset management", "asset manager", "wealth management",
        "fixed income", "portfolio", "endowment", "pension",
        "mutual fund", "etf",
    ],
    "Sales & Trading": [
        "sales and trading", "s&t", "trading", "markets",
        "derivatives", "swaps", "commodities", "rates",
    ],
    "Management Consulting": [
        "consulting", "consultant", "strategy consulting",
        "management consulting", "mbb", "advisory",
    ],
    "Corp Dev / M&A": [
        "corporate development", "corp dev", "m&a", "strategic finance",
        "strategic planning",
    ],
    "FP&A / Finance": [
        "fp&a", "financial planning", "financial analysis",
        "finance associate", "finance intern", "finance rotational",
        "treasury", "corporate finance",
    ],
    "Strategy & Ops / BizOps": [
        "strategy", "operations", "biz ops", "bizops",
        "business operations", "strategic operations",
        "strategy and operations",
    ],
    "Data / Analytics": [
        "data analyst", "data analytics", "business analyst",
        "business intelligence", "bi analyst", "reporting analyst",
    ],
    "Rotational": [
        "rotational", "rotation program", "leadership development",
        "finance leadership",
    ],
}
