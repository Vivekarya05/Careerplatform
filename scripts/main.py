"""
Daily pipeline entry point:
  1. Load your master profile
  2. Fetch fresh jobs from Adzuna + Jooble for your target titles/locations
  3. Skip jobs already seen in a previous run
  4. Score each new job against your skills
  5. For jobs above the match threshold, tailor a resume + cover letter via Claude
  6. Write everything the dashboard needs into docs/data/jobs.json
"""

import json
import os

from fetch_jobs import fetch_all_jobs
from match_engine import score_job
from tailor_documents import tailor_and_render

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(ROOT, "data", "master_profile.json")
JOBS_OUT_PATH = os.path.join(ROOT, "docs", "data", "jobs.json")
SEEN_PATH = os.path.join(ROOT, "docs", "data", "seen_jobs.json")
DOWNLOADS_DIR = os.path.join(ROOT, "docs", "downloads")


def load_json(path: str, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    profile = load_json(PROFILE_PATH, {})
    seen_ids = set(load_json(SEEN_PATH, []))
    existing_jobs = load_json(JOBS_OUT_PATH, [])

    print("Fetching jobs...")
    jobs = fetch_all_jobs(profile["target_titles"], profile["target_locations"])
    print(f"Found {len(jobs)} jobs total, {len(seen_ids)} already seen before.")

    new_results = []
    threshold = profile.get("min_match_score_to_tailor", 40)

    for job in jobs:
        if job["id"] in seen_ids:
            continue
        seen_ids.add(job["id"])

        match = score_job(job["description"], profile["core_skills"])
        record = {**job, **match, "resume_file": None, "cover_letter_file": None}

        if match["match_score"] >= threshold:
            try:
                print(f"Tailoring documents for: {job['title']} @ {job['company']} "
                      f"(match {match['match_score']}%)")
                docs = tailor_and_render(profile, job, DOWNLOADS_DIR)
                record.update(docs)
            except Exception as e:
                print(f"Failed to tailor documents for {job['id']}: {e}")

        new_results.append(record)

    all_jobs = new_results + existing_jobs
    save_json(JOBS_OUT_PATH, all_jobs)
    save_json(SEEN_PATH, list(seen_ids))

    print(f"Done. {len(new_results)} new jobs processed this run.")


if __name__ == "__main__":
    main()
