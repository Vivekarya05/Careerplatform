create extension if not exists pgcrypto;

create type job_status as enum ('new', 'saved', 'ignored', 'applied', 'interviewing', 'closed');
create type relationship_stage as enum (
  'new',
  'reached_out',
  'replied',
  'call_scheduled',
  'interview',
  'opportunity_active',
  'closed'
);

create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  location text not null default 'Sydney, Australia',
  target_roles text[] not null default '{}',
  skills text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  company text not null,
  location text,
  source text not null,
  url text,
  description text not null default '',
  salary_min integer,
  salary_max integer,
  posted_at date,
  status job_status not null default 'new',
  score integer not null default 0 check (score between 0 and 100),
  score_breakdown jsonb not null default '{}'::jsonb,
  content_hash text generated always as (
    encode(digest(lower(coalesce(title, '') || '|' || coalesce(company, '') || '|' || coalesce(url, '')), 'sha256'), 'hex')
  ) stored,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, content_hash)
);

create table applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  job_id uuid not null references jobs(id) on delete cascade,
  status text not null default 'draft',
  applied_at timestamptz,
  resume_version_id uuid,
  cover_letter_version_id uuid,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table recruiters (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  email text,
  company text,
  linkedin text,
  focus_area text,
  relationship_stage relationship_stage not null default 'new',
  response_status text,
  last_contact date,
  followup_due date,
  quality_score integer not null default 50 check (quality_score between 0 and 100),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table resume_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  job_id uuid references jobs(id) on delete set null,
  title text not null,
  latex_source text not null,
  pdf_storage_path text,
  ats_score integer check (ats_score between 0 and 100),
  strategy jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table email_drafts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  recruiter_id uuid references recruiters(id) on delete set null,
  job_id uuid references jobs(id) on delete set null,
  type text not null,
  subject text not null,
  body text not null,
  approved_at timestamptz,
  sent_at timestamptz,
  created_at timestamptz not null default now()
);

alter table profiles enable row level security;
alter table jobs enable row level security;
alter table applications enable row level security;
alter table recruiters enable row level security;
alter table resume_versions enable row level security;
alter table email_drafts enable row level security;

create policy "profile owner access" on profiles for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "job owner access" on jobs for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "application owner access" on applications for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "recruiter owner access" on recruiters for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "resume owner access" on resume_versions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "email draft owner access" on email_drafts for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create index jobs_user_score_idx on jobs(user_id, score desc);
create index jobs_user_status_idx on jobs(user_id, status);
create index recruiters_followup_idx on recruiters(user_id, followup_due);
create index applications_user_status_idx on applications(user_id, status);

