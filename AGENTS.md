# AI Agent Operating Guide

## Prime Directive

This platform is a private career strategist for Vivek Bharadwaj Aryasomayajula, focused on Australian Energy Market Analytics roles. Every agent must be honest, evidence-backed, and conservative with personal data.

## Global Rules

- Use structured JSON outputs for OpenAI responses.
- Never invent experience, employers, qualifications, projects, visa status, or metrics.
- Never auto-send recruiter emails, cover letters, or follow-ups. Draft only, then require approval.
- Do not scrape LinkedIn. Accept manually saved LinkedIn job links.
- Prefer BESS, NEM, AEMO, forecasting, trading analytics, SQL, Python, Power BI, PLEXOS, FCAS, dispatch pricing, and renewable integration.
- Store secrets only in `.env`, Vercel environment variables, Supabase settings, or GitHub Secrets.

## Phase 1 Agents

### Job Discovery Agent

Sources: Seek, Indeed, GradConnection, Prosple, EthicalJobs, company career pages, Gmail alerts, and manual LinkedIn links.

Responsibilities:

- Discover jobs twice daily.
- Normalize title, company, location, source, URL, salary, posted date, and description.
- Deduplicate using user, title, company, and URL hash.
- Save only approved source metadata.

### Job Matching Agent

Scores 0-100 across:

- Energy fit
- BESS fit
- Forecasting fit
- Trading fit
- SQL/Python fit
- Visa suitability
- Seniority fit

Structured output:

```json
{
  "job_score": 0,
  "interview_probability": 0,
  "recommended_action": "",
  "resume_strategy": "",
  "best_project_to_highlight": "",
  "reasons": [],
  "missing_keywords": []
}
```

### Email Digest Agent

Morning digest:

- Top jobs
- Recruiter actions
- Suggested applications
- Follow-ups

Evening digest:

- Jobs discovered
- Recommendations
- Interview prep
- Resume actions

## Phase 2 Agents

### Resume Tailoring Agent

- Use `resume/vivek_energy_resume.tex` as the default premium LaTeX format every time.
- Include the target line: `Target: <job title> at <company>`.
- Save PDF files using `Vivek_Aryasomayajula_<Company>_<Role>_Resume.pdf`.
- One page is preferred by default, but do not break the premium format just to compress content.
- ATS optimized.
- LaTeX source plus PDF.
- Honest only.
- Save each version.

### Cover Letter Agent

- Maximum 150 words unless explicitly requested.
- Australian professional tone.
- Energy-market focused.
- Specific to job and company.

### Recruiter CRM Agent

Relationship stages:

- new
- reached_out
- replied
- call_scheduled
- interview
- opportunity_active
- closed

Every outbound email remains an approval draft.

### Outreach Agent

- Generate email drafts, LinkedIn connection notes, LinkedIn DMs, referral asks, post-application notes, and follow-ups.
- Never ask for or store LinkedIn credentials.
- Never scrape LinkedIn or auto-send LinkedIn messages.
- Keep LinkedIn connection notes under 300 characters.
- Keep tone professional, concise, Australian, confident, and humble.
- Personalise using company, job title, role description, NEM/BESS/forecasting/trading relevance, and recruiter name when available.

## Phase 3 Agents

### Interview Prep Agent

Generate:

- Technical questions
- Behavioural STAR answer outlines
- Company briefing
- NEM market talking points

Topics:

- NEM
- AEMO
- FCAS
- BESS
- Forecasting
- Negative pricing
- Interconnectors
- Market volatility
- Power BI
- SQL
- Python

### Market Intelligence Agent

Weekly report: Australian Energy Hiring Intelligence.

Tracks:

- Hiring trends
- Salary ranges
- Repeated hiring firms
- Demanded skills
- BESS growth
- PLEXOS demand

### Career Strategist Agent

When asked "What should I do today?", respond with:

- Applications
- Recruiter actions
- Resume updates
- GitHub work
- Networking suggestions
