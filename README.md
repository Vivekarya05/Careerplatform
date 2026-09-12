# Career platform

Finds jobs matching your skills, scores the match, and generates a tailored,
ATS-friendly resume + cover letter for each one — automatically, once a day,
hosted entirely on GitHub for free (aside from the small Anthropic API cost).

## Before you do anything else

Open `data/master_profile.json` and fix every field marked `VERIFY`. Two of
your existing resume versions and your LinkedIn profile disagreed on the
Western Sydney University job title and on your PG Diploma's institution
name and dates — get the correct wording from your actual contracts and
transcripts before this file starts generating applications for you.

## How it works

1. **GitHub Actions** runs `scripts/main.py` once a day on a free scheduled
   runner — no server to maintain.
2. **`fetch_jobs.py`** pulls listings from the Adzuna and Jooble APIs for
   your target titles/locations. (Note: SEEK and LinkedIn don't offer public
   search APIs, and scraping them would breach their terms of service, so
   they're intentionally not included here.)
3. **`match_engine.py`** scores each new job against your skills and lists
   what matches and what's missing.
4. **`tailor_documents.py`** calls the Anthropic API for jobs above your
   match threshold, and writes a tailored resume + cover letter as `.docx`.
5. **`docs/`** is a static dashboard (served by GitHub Pages) that reads the
   results and lets you browse, compare, and download.

## Setup

### 1. Create the repo
Create a new **public** GitHub repo (public repos get unlimited free Actions
minutes and free Pages hosting) and push everything in this folder to it.

### 2. Get your API keys (all have free tiers except Anthropic)
- Adzuna: https://developer.adzuna.com/ (free, instant signup)
- Jooble: https://jooble.org/api/about (free, instant signup)
- Anthropic: https://console.anthropic.com/ (pay-as-you-go — tailoring one
  job with the default model costs a fraction of a cent to a few cents)

### 3. Add the keys as repo secrets
Repo → **Settings → Secrets and variables → Actions → New repository
secret**. Add all four:
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `JOOBLE_API_KEY`
- `ANTHROPIC_API_KEY`

### 4. Enable GitHub Pages
Repo → **Settings → Pages** → Source: "Deploy from a branch" → Branch:
`main` → Folder: `/docs` → Save. Your dashboard will be live at
`https://<your-username>.github.io/<repo-name>/`.

### 5. Test it locally first (recommended)
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your real keys
export $(cat .env | xargs)
cd scripts
python main.py
```
Check `docs/data/jobs.json` and `docs/downloads/` before trusting the daily
automation with it.

### 6. Let it run
The workflow runs automatically every day (`.github/workflows/daily-job-search.yml`).
You can also trigger it manually any time: repo → **Actions** →
"Daily job search" → **Run workflow**.

## Tuning it to you

- `target_titles` / `target_locations` in `data/master_profile.json` —
  widen or narrow your search.
- `min_match_score_to_tailor` — raise this if you're getting too many
  low-relevance tailored documents; lower it to see more borderline matches
  (untailored) on the dashboard.
- `scripts/tailor_documents.py` — the `MODEL` constant defaults to Claude
  Haiku 4.5 for cost efficiency running daily at scale. Swap to
  `claude-sonnet-5` if you want higher-quality tailoring and don't mind the
  extra cost per job.

## Honest limitations (v1)

- Skill matching is keyword-based, not semantic — it won't catch a JD that
  says "reporting tools" instead of "Power BI." Good enough to triage; a
  natural upgrade later is embedding-based matching.
- Adzuna/Jooble field names in `fetch_jobs.py` are based on their published
  docs — verify against the live API response the first time you run it, as
  public APIs occasionally change shape.
- No email/notification step yet — you check the dashboard. Easy to add
  later (e.g. a GitHub Actions step that emails a daily digest).
