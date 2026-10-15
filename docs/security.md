# Security Guide

## Credential Handling

- Never commit `.env`, `.env.local`, service role keys, Gmail app passwords, or OpenAI keys.
- Use GitHub Secrets for scheduler credentials.
- Use Vercel environment variables for frontend public config only.
- Keep Supabase service role keys backend-only.
- Use the anon key only in the frontend.
- Treat `CAREER_USER_ID` as private operational metadata, not as a public profile id.

## Authentication

- Production requires Supabase Auth.
- Database access must use RLS policies.
- Backend routes require bearer authentication outside local development.

## Data Rules

- Store only job-search-relevant personal data.
- Do not store raw Gmail passwords. Use app passwords or OAuth tokens.
- Do not scrape LinkedIn.
- Do not ask for or store LinkedIn credentials. Generate LinkedIn messages as drafts for manual sending only.
- Store manually submitted LinkedIn URLs as user-provided records only.

## AI Safety

- Resume and cover letter agents must not hallucinate experience.
- Recruiter outreach must require approval before sending.
- Structured JSON outputs are required for agent decisions.
- Keep generated drafts auditable by saving versions.

## Repository

- Keep the GitHub repo private.
- Require branch protection before production use.
- Rotate credentials if a secret is ever pasted into chat, logs, commits, or screenshots.
