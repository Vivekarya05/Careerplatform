"""
Fetches job listings from Adzuna and Jooble for the target titles/locations
defined in data/master_profile.json.

Docs (verify field names against these before relying on this in production —
public APIs change their response shape over time):
  Adzuna: https://developer.adzuna.com/docs/search
  Jooble: https://jooble.org/api/about
"""

import os
import requests

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs/au/search/1"
JOOBLE_BASE = "https://jooble.org/api/{key}"


def fetch_adzuna(query: str, location: str, results: int = 20) -> list[dict]:
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        print("Adzuna credentials missing, skipping Adzuna.")
        return []

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results,
        "what": query,
        "where": location,
        "content-type": "application/json",
    }
    resp = requests.get(ADZUNA_BASE, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("results", []):
        jobs.append({
            "id": f"adzuna_{item.get('id')}",
            "source": "adzuna",
            "title": item.get("title", "").strip(),
            "company": (item.get("company") or {}).get("display_name", "Unknown"),
            "location": (item.get("location") or {}).get("display_name", location),
            "description": item.get("description", ""),
            "url": item.get("redirect_url", ""),
            "salary_min": item.get("salary_min"),
            "salary_max": item.get("salary_max"),
        })
    return jobs


def fetch_jooble(query: str, location: str) -> list[dict]:
    api_key = os.environ.get("JOOBLE_API_KEY")
    if not api_key:
        print("Jooble credentials missing, skipping Jooble.")
        return []

    url = JOOBLE_BASE.format(key=api_key)
    payload = {"keywords": query, "location": location}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("jobs", []):
        jobs.append({
            "id": f"jooble_{item.get('id') or item.get('link')}",
            "source": "jooble",
            "title": (item.get("title") or "").strip(),
            "company": item.get("company", "Unknown"),
            "location": item.get("location", location),
            "description": item.get("snippet", ""),
            "url": item.get("link", ""),
            "salary_min": None,
            "salary_max": None,
        })
    return jobs


def fetch_all_jobs(target_titles: list[str], target_locations: list[str]) -> list[dict]:
    """Runs every title x location combination against both sources and dedupes by id."""
    all_jobs = {}
    for title in target_titles:
        for location in target_locations:
            for job in fetch_adzuna(title, location) + fetch_jooble(title, location):
                if job["id"] not in all_jobs:
                    all_jobs[job["id"]] = job
    return list(all_jobs.values())
