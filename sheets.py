"""
Google Sheets integration for the job hunt dashboard.
Uses the gspread library + a service account JSON key.

Setup (one-time, ~10 min):
  1. Go to https://console.cloud.google.com
  2. Create a project → Enable "Google Sheets API" + "Google Drive API"
  3. IAM & Admin → Service Accounts → Create service account
  4. Keys tab → Add Key → JSON → download as service_account.json
  5. Put service_account.json in your project root (next to main.py)
  6. Create a new Google Sheet, share it with the service account email
     (looks like: name@project.iam.gserviceaccount.com) — give it Editor access
  7. Copy the Sheet ID from its URL:
     https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
  8. Paste SHEET_ID into config.py → GOOGLE_SHEET_ID

Then run:  pip install gspread google-auth
"""

import os
import json
from datetime import datetime
from typing import Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

from scrapers.base import JobPosting

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Tab names
TAB_TODAY     = "Today's New Postings"
TAB_WATCHLIST = "Apply This Week"
TAB_APPLIED   = "Applied"
TAB_ALUMNI    = "Alumni Pipeline"
TAB_LOG       = "Run Log"

HEADERS = [
    "Fit Score", "Company", "Role Title", "Category", "Location",
    "Source", "Posted Date", "Deadline", "Sponsors Intl?",
    "Why It Fits", "Apply URL", "First Seen", "Status"
]


def _get_client(service_account_path: str = "service_account.json"):
    if not GSPREAD_AVAILABLE:
        raise ImportError(
            "gspread not installed. Run:  pip install gspread google-auth"
        )
    if not os.path.exists(service_account_path):
        raise FileNotFoundError(
            f"Service account key not found at: {service_account_path}\n"
            "Follow the setup instructions in sheets.py"
        )
    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return gspread.authorize(creds)


def _ensure_tab(spreadsheet, tab_name: str, headers: list[str]):
    """Create tab if it doesn't exist, write headers if empty."""
    try:
        ws = spreadsheet.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(headers))

    existing = ws.get_all_values()
    if not existing or existing[0] != headers:
        ws.clear()
        ws.append_row(headers, value_input_option="USER_ENTERED")
    return ws


def _job_to_row(job: JobPosting, today: str) -> list:
    return [
        getattr(job, "fit_score", ""),
        job.company,
        job.title,
        getattr(job, "category", ""),
        job.location,
        job.source,
        job.posted_date or "",
        getattr(job, "deadline", ""),
        getattr(job, "sponsors_intl", "Unknown"),
        getattr(job, "why_it_fits", ""),
        job.url,
        today,
        "New",
    ]


def push_to_sheets(
    jobs: list[JobPosting],
    sheet_id: str,
    service_account_path: str = "service_account.json",
    verbose: bool = True,
) -> bool:
    """
    Push filtered jobs to Google Sheets.
    - Deduplicates against existing rows (by Company + Title + Location).
    - Writes new rows to TAB_TODAY, clears and rewrites it each run.
    - Appends genuinely new rows to TAB_WATCHLIST (7+ fit score only).
    - Appends a run summary row to TAB_LOG.
    Returns True on success, False on any error.
    """
    if not sheet_id or sheet_id == "PASTE_YOUR_SHEET_ID_HERE":
        print("⚠️  Google Sheets: SHEET_ID not configured in config.py. Skipping.")
        return False

    try:
        gc = _get_client(service_account_path)
        spreadsheet = gc.open_by_key(sheet_id)
    except Exception as e:
        print(f"⚠️  Google Sheets connection failed: {e}")
        return False

    today = datetime.now().strftime("%Y-%m-%d")

    # ── Today's New Postings tab (full refresh each run) ──────────────────
    ws_today = _ensure_tab(spreadsheet, TAB_TODAY, HEADERS)
    ws_today.clear()
    ws_today.append_row(HEADERS, value_input_option="USER_ENTERED")

    rows = [_job_to_row(j, today) for j in jobs]
    if rows:
        ws_today.append_rows(rows, value_input_option="USER_ENTERED")

    # ── Apply This Week tab (append 7+ scores, dedup by URL) ─────────────
    ws_watch = _ensure_tab(spreadsheet, TAB_WATCHLIST, HEADERS)
    existing_urls = set()
    try:
        existing_rows = ws_watch.get_all_values()[1:]  # skip header
        url_col_idx = HEADERS.index("Apply URL")
        existing_urls = {r[url_col_idx] for r in existing_rows if len(r) > url_col_idx}
    except Exception:
        pass

    high_fit = [j for j in jobs if getattr(j, "fit_score", 0) >= 7]
    new_high_fit = [j for j in high_fit if j.url not in existing_urls]
    if new_high_fit:
        ws_watch.append_rows(
            [_job_to_row(j, today) for j in new_high_fit],
            value_input_option="USER_ENTERED",
        )

    # ── Ensure other tabs exist ───────────────────────────────────────────
    _ensure_tab(spreadsheet, TAB_APPLIED, [
        "Company", "Role Title", "Date Applied", "Status",
        "Follow-Up Date", "Contact", "Notes", "Apply URL"
    ])
    _ensure_tab(spreadsheet, TAB_ALUMNI, [
        "Name", "Company", "Title", "School", "LinkedIn URL",
        "Outreach Status", "Response", "Next Action", "Notes"
    ])

    # ── Run log ───────────────────────────────────────────────────────────
    ws_log = _ensure_tab(spreadsheet, TAB_LOG, [
        "Run Date", "Total Jobs", "Relevant Jobs", "High Fit (7+)",
        "New to Watchlist", "Sources"
    ])
    sources = list({j.source for j in jobs})
    ws_log.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "",  # total filled by main.py
        len(jobs),
        len(high_fit),
        len(new_high_fit),
        ", ".join(sorted(sources)),
    ])

    if verbose:
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
        print(f"\n📊 Google Sheets updated → {sheet_url}")
        print(f"   {len(jobs)} jobs written to '{TAB_TODAY}'")
        print(f"   {len(new_high_fit)} new high-fit jobs added to '{TAB_WATCHLIST}'")

    return True
