"""Small Adzuna client used by the API; credentials stay server-side."""

from dataclasses import dataclass
from functools import lru_cache
from html import unescape
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from matching.sample_jobs import JobListing

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/us/search"


class JobSearchError(RuntimeError):
    """Raised when live jobs cannot be retrieved from Adzuna."""


def load_local_environment() -> None:
    """Load simple KEY=VALUE entries from the project .env without overriding env vars."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def configured() -> bool:
    load_local_environment()
    return (
        os.getenv("ADZUNA_ENABLED", "false").casefold() == "true"
        and bool(os.getenv("ADZUNA_APP_ID") and os.getenv("ADZUNA_APP_KEY"))
    )


def clean_description(value: str) -> str:
    """Adzuna descriptions may contain HTML; return plain text for embeddings/UI."""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def to_job_listing(ad: dict) -> JobListing:
    company = ad.get("company") or {}
    location = ad.get("location") or {}
    return JobListing(
        title=clean_description(ad.get("title", "Untitled role")),
        company=clean_description(company.get("display_name", "Company not listed")),
        location=clean_description(location.get("display_name", "Location not listed")),
        description=clean_description(ad.get("description", "No description provided.")),
        application_url=ad.get("redirect_url", ""),
    )


@lru_cache(maxsize=64)
def search_jobs(query: str, location: str, page: int = 1) -> tuple[JobListing, ...]:
    """Retrieve one cached page of current U.S. jobs from Adzuna."""
    if not configured():
        raise JobSearchError("Live job search is not configured on this server.")

    parameters = urlencode(
        {
            "app_id": os.environ["ADZUNA_APP_ID"],
            "app_key": os.environ["ADZUNA_APP_KEY"],
            "what": query,
            "where": location,
            "results_per_page": 20,
            "content-type": "application/json",
        }
    )
    request = Request(
        f"{ADZUNA_API_URL}/{page}?{parameters}",
        headers={"Accept": "application/json", "User-Agent": "AI-Career-Coach/1.0"},
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise JobSearchError("The job provider rejected this search. Please try again.") from error
    except (URLError, TimeoutError) as error:
        raise JobSearchError("The job provider could not be reached. Please try again.") from error

    return tuple(to_job_listing(ad) for ad in payload.get("results", []))
