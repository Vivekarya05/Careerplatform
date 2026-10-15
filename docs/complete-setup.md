# Complete Setup Checklist

## Already Done

- GitHub repo contains the full platform.
- Vercel dashboard is live at `https://jobsearch-ai-beta.vercel.app/`.
- Dashboard builds from `frontend/`.
- Backend has Supabase persistence with local demo fallback.
- Scheduler runs at 8 AM and 6 PM Sydney time once secrets are configured.

## Supabase

Create a Supabase project, then run:

```text
database/schema.sql
```

Enable Auth:

- Provider: Email
- Magic links: enabled
- Site URL: `https://jobsearch-ai-beta.vercel.app`
- Redirect URL: `https://jobsearch-ai-beta.vercel.app`

Collect:

- Project URL
- Anon key
- Service role key
- JWT secret
- Your user id from `auth.users`

## Backend Hosting

Deploy the backend with Render:

- Connect repo: `Vivekarya05/jobsearchAI`
- Root directory: `backend`
- Build command: `pip install -e .`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Environment variables:

```text
APP_ENV=production
ALLOWED_ORIGINS=https://jobsearch-ai-beta.vercel.app
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_SECRET=...
CAREER_USER_ID=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
RESEND_API_KEY=...
EMAIL_FROM=Career Intelligence <your_verified_sender>
EMAIL_TO=your_email
RESUME_STORAGE_BUCKET=resumes
```

Create a private Supabase storage bucket named `resumes` for generated PDFs.

## Vercel Frontend Variables

Set these in Vercel project settings:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-render-backend-url
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

Redeploy Vercel after saving.

## GitHub Actions Secrets

Add:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
CAREER_USER_ID
OPENAI_API_KEY
OPENAI_MODEL
RESEND_API_KEY
EMAIL_FROM
EMAIL_TO
GMAIL_IMAP_USER
GMAIL_IMAP_APP_PASSWORD
```

Then run the `Career Intelligence Scheduler` workflow manually from GitHub Actions.
