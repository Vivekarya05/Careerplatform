# Career platform — system architecture

## 1. Design philosophy

Everything here is chosen to avoid running or paying for a server:
- **GitHub Actions** provides the only "compute" — a free, ephemeral virtual
  machine that spins up once a day, runs the pipeline, and disappears.
- **GitHub Pages** provides hosting — a static file server with no backend,
  no database, and nothing to patch or maintain.
- **Your resume content lives in one file** (`data/master_profile.json`) so
  every tailored document is generated from the same source of truth instead
  of being hand-edited each time.

The trade-off: nothing here is "live" in the sense of a real-time app. Data
only updates once a day (or when you manually trigger a run), and the
dashboard only ever shows what was true as of the last commit.

## 2. Where each part actually runs

| Component | Runs on | Lifetime | Has internet access | Has your API keys |
|---|---|---|---|---|
| `scripts/*.py` | GitHub Actions runner (Ubuntu VM) | ~1-3 min, once/day | Yes | Yes (injected as env vars) |
| `docs/*.html/css/js` | Your browser | While the tab is open | Only to fetch `jobs.json` and `.docx` files from the same site | No — never exposed |
| Adzuna, Jooble, Anthropic APIs | Their own servers | N/A | — | Receives requests, doesn't store your keys |
| `data/master_profile.json` | Committed to the repo | Persistent | — | — |

This split matters for one reason: **your API keys never touch the public
website.** They only ever exist as encrypted GitHub secrets, injected into
the Actions runner's environment for the few minutes it runs, then gone. The
dashboard your browser loads has no way to see them.

## 3. Component responsibilities

**`scripts/fetch_jobs.py`** — calls Adzuna and Jooble for every
(target title × target location) pair, normalizes both into one shape, and
deduplicates. If a key is missing it skips that source and logs a warning
rather than crashing the whole run.

**`scripts/match_engine.py`** — pure function, no external calls. Extracts a
known vocabulary of skill terms from the job description text and compares
it against your `core_skills`. Returns a 0-100 score plus matched/missing
lists. This runs on *every* new job, cheaply, before anything expensive
happens.

**`scripts/tailor_documents.py`** — the only component that costs money.
Only runs for jobs that clear `min_match_score_to_tailor`. Sends your
profile + the JD to the Anthropic API, gets back structured JSON, and
renders it into two `.docx` files with `python-docx`.

**`scripts/main.py`** — orchestrator. Owns the sequencing and the
"don't reprocess a job twice" logic via `docs/data/seen_jobs.json`. This
file is the only thing standing between you and re-paying the Anthropic API
for the same job every single day — treat it as important state.

**`.github/workflows/daily-job-search.yml`** — defines *when* `main.py`
runs and *what secrets* it's allowed to see. After the script finishes, this
workflow commits `docs/data/` and `docs/downloads/` back to the repo — that
commit is the only mechanism by which new results reach the live dashboard.

**`docs/index.html` + `app.js`** — has zero logic beyond "fetch
`data/jobs.json`, render cards, filter by the slider." No build step, no
framework — kept deliberately simple so there's nothing to break.

## 4. Sequence of one daily run

1. Cron fires (or you click "Run workflow" manually) → GitHub spins up a
   fresh Ubuntu VM.
2. Runner checks out the repo, installs `requirements.txt`.
3. `main.py` loads `master_profile.json` and `seen_jobs.json`.
4. `fetch_jobs.py` queries Adzuna + Jooble for each title/location pair.
5. Job IDs already in `seen_jobs.json` are dropped; only genuinely new
   listings continue.
6. Each new job is scored by `match_engine.py`.
7. Jobs at or above your threshold go to `tailor_documents.py` → one
   Anthropic API call each → two `.docx` files written to
   `docs/downloads/`.
8. `docs/data/jobs.json` and `docs/data/seen_jobs.json` are rewritten.
9. The workflow commits and pushes those two folders.
10. Next time anyone loads the Pages URL, their browser fetches the
    freshly-committed `jobs.json` and renders it — this is the *only* path
    data takes to reach the live site.

## 5. Data shape (one entry in `docs/data/jobs.json`)

```json
{
  "id": "adzuna_123456",
  "source": "adzuna",
  "title": "Business Analyst",
  "company": "Example Energy Co",
  "location": "Sydney NSW",
  "url": "https://...",
  "salary_min": 95000,
  "salary_max": 120000,
  "match_score": 62.5,
  "matched_skills": ["SQL", "Power BI", "Stakeholder Management"],
  "missing_skills": ["Tableau", "Agile"],
  "resume_file": "ExampleEnergyCo_BusinessAnalyst_resume.docx",
  "cover_letter_file": "ExampleEnergyCo_BusinessAnalyst_cover_letter.docx"
}
```

## 6. Security and privacy decision you should make now

Your repo needs to be **public** for GitHub Pages to be free — private-repo
Pages requires GitHub Pro (~$4/month). Being public means anyone with the
link can see `data/master_profile.json` (your resume content) and browse
your job-match dashboard.

Since this content already mirrors what's public on your LinkedIn and
resumes, that's a reasonable trade for most people — but it's your call.
Options if you'd rather not:
- Keep the repo public, but don't share the Pages URL — it isn't indexed or
  discoverable unless someone has the exact link or finds the repo.
- Pay for GitHub Pro and make the repo private.
- Skip Pages entirely and just read `docs/data/jobs.json` locally instead
  of hosting a dashboard.

Your API keys are safe either way — they're GitHub Actions secrets, not
repo content, and are never exposed regardless of the repo's visibility.

## 7. Cost breakdown

| Item | Cost |
|---|---|
| GitHub (public repo, Actions, Pages) | $0 |
| Adzuna API | $0 (free tier) |
| Jooble API | $0 (free tier) |
| Anthropic API (Claude Haiku 4.5) | ~$0.01-0.05 per tailored job — realistically $1-5/month |

## 8. Known limitations (v1) and natural next upgrades

- Matching is keyword overlap, not semantic — won't catch a JD that says
  "reporting tools" instead of "Power BI." Upgrade path: embeddings.
- No notifications — you have to check the dashboard. Upgrade path: an
  extra workflow step that emails a daily digest.
- No retry logic if an API call fails mid-run — that one job is just
  skipped and logged. Fine for a personal tool; would need hardening for
  anything more serious.
- SEEK and LinkedIn are intentionally excluded (no public API, and scraping
  would breach their terms of service).
