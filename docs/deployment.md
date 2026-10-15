# Deployment Guide

## 1. Supabase

1. Create a Supabase project.
2. Run `database/schema.sql` in the SQL editor.
3. Confirm RLS is enabled on all user-owned tables.
4. Create a private storage bucket for generated resumes.
5. Enable email magic-link auth.
6. Add `https://jobsearch-ai-beta.vercel.app` to allowed redirect URLs.
7. Copy the project URL, anon key, JWT secret, and service role key.
8. After your user signs in once, copy your `auth.users.id` value as `CAREER_USER_ID`.

## 2. Backend

Recommended hosting options:

- Render
- Fly.io
- Railway
- Google Cloud Run

Set environment variables from `backend/.env.example`.

Required backend variables:

- `APP_ENV=production`
- `PUBLIC_ACCESS_ENABLED=false`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `CAREER_USER_ID`
- `ALLOWED_ORIGINS=https://jobsearch-ai-beta.vercel.app`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `EMAIL_TO`
- `RESUME_STORAGE_BUCKET=resumes`

Optional but strongly recommended for Australian live job discovery:

- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `DISCOVERY_LOCATION=Australia`
- `DISCOVERY_COUNTRIES=Australia,India`
- `DISCOVERY_RESULTS_PER_SOURCE=12`
- `COMPANY_CAREER_SOURCES=AEMO|https://www.aemo.com.au/en/about/careers,JD Ross Energy|https://www.jdrossenergy.com/,Phillip Riley|https://www.phillipriley.com.au/`

Without Adzuna, the platform still runs company career pages and no-key public feeds, but Australian Energy/NEM/BESS coverage will be weaker. Adzuna improves live Australia-specific discovery without scraping LinkedIn.

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 3. Frontend

Deploy `frontend/` to Vercel.

Required variables:

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_REQUIRE_AUTH=true`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Temporary no-login mode:

- Render: set `PUBLIC_ACCESS_ENABLED=true`
- Vercel: set `NEXT_PUBLIC_REQUIRE_AUTH=false`

Use this only while validating the platform. Anyone with the dashboard URL can use the live backend in this mode, including AI-backed actions.

## 4. GitHub Actions

Create a private GitHub repository and add these secrets:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `CAREER_USER_ID`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `EMAIL_TO`
- `GMAIL_IMAP_USER`
- `GMAIL_IMAP_APP_PASSWORD`
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`

The workflow runs hourly and executes only at 8 AM and 6 PM Sydney time.

For a test email, manually run the workflow and choose `test` as the period.

## 5. Email

Use Resend for digests. Gmail SMTP or Gmail API can be added for inbound recruiter alert parsing, but outbound recruiter messages must stay draft-only until explicitly approved.

## Current Recommended Order

1. Create Supabase and run `database/schema.sql`.
2. Set Vercel frontend variables for Supabase.
3. Deploy the backend on Render using `render.yaml`.
4. Set `NEXT_PUBLIC_API_BASE_URL` in Vercel to the Render backend URL.
5. Add GitHub Actions secrets and run the scheduler manually once.
6. Add job-source credentials and Gmail parsing after the core loop is verified.
