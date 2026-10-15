# Career Intelligence Platform

Private AI-powered career operating system for Vivek Bharadwaj Aryasomayajula's
Business-Analyst-in-Energy job search in Australia — combining career coach,
job intelligence engine, resume writer, recruiter strategist, skill-gap
tracker, and interview mentor in one platform.

Positioning: **Business Analyst IN Energy**, not Business Analyst OR Energy.

## Architecture

- **Frontend**: Next.js + TypeScript, mobile-friendly dashboard (`frontend/`)
- **Backend**: Python FastAPI with agent services (`backend/`)
- **Database**: Supabase PostgreSQL with RLS (`database/`)
- **Auth**: Supabase Auth magic-link sign-in
- **Storage**: Supabase Storage for generated resumes
- **AI**: OpenAI API with structured JSON outputs
- **Resume PDFs**: LaTeX (`resume/`) compiled with `latexmk`
- **Scheduler**: GitHub Actions cron, twice-daily job discovery + digest
- **Email digest**: Resend API
- **Your source-of-truth profile**: [`data/master_profile.json`](data/master_profile.json)

See [`docs/complete-setup.md`](docs/complete-setup.md), [`docs/deployment.md`](docs/deployment.md)
and [`docs/security.md`](docs/security.md) for full setup, deployment, and
security details, and [`AGENTS.md`](AGENTS.md) for what each agent does and
the safety rules they operate under.

## Repo structure

```text
backend/              FastAPI API, services, agents, CLI
frontend/             Next.js + TypeScript dashboard
agents/               Cross-agent specs and prompts
resume/               LaTeX resume template
database/             Supabase schema and seed files
data/                 Your master profile (source of truth for resume content)
.github/workflows/    Scheduled job discovery + digest
tests/                Unit tests
docs/                 Deployment and security docs
```

## Before you do anything else

Open [`data/master_profile.json`](data/master_profile.json) and fix every
field marked `VERIFY` — your existing resume versions and LinkedIn disagree
on a couple of dates and institution names.

## Run it locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
uvicorn app.main:app --reload
```

With `APP_ENV=development` and no `SUPABASE_JWT_SECRET` set, the backend
runs against an in-memory job store — no Supabase project required to try it
out locally.

### Frontend

```bash
cd frontend
cp .env.example .env.local
# set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
# set NEXT_PUBLIC_REQUIRE_AUTH=false for local testing without Supabase Auth
npm install
npm run dev
```

Visit `http://localhost:3000`.

## Going live

1. Create a Supabase project, run `database/schema.sql` then `database/seed.sql`.
2. Get free-tier API keys: [Adzuna](https://developer.adzuna.com/), and a
   pay-as-you-go [OpenAI](https://platform.openai.com/) key.
3. Deploy the backend to Render (`render.yaml` is already set up) and the
   frontend to Vercel, wiring in the environment variables listed in
   [`docs/deployment.md`](docs/deployment.md).
4. Add the same secrets as GitHub Actions secrets so the scheduled job
   discovery + digest workflow (`.github/workflows/career-intelligence.yml`)
   can run twice daily.

## Safety rules

- No hardcoded credentials.
- No LinkedIn scraping — manual LinkedIn links/descriptions only.
- No fabricated experience, employers, or metrics.
- Recruiter/outreach messages are drafts only — never auto-sent.
- Keep the repository private in production.
