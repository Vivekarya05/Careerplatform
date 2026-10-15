export type JobStatus = "new" | "saved" | "ignored" | "applied" | "interviewing" | "closed";

export type Job = {
  id: string;
  title: string;
  company: string;
  location: string;
  source: string;
  url?: string;
  description?: string;
  salary_min?: number;
  salary_max?: number;
  posted_at?: string;
  created_at?: string;
  updated_at?: string;
  status: JobStatus;
  score: number;
  score_breakdown: {
    interview_probability?: number;
    recommended_action?: string;
    resume_strategy?: string;
    best_project_to_highlight?: string;
    reasons?: string[];
    missing_keywords?: string[];
    salary_estimate?: string;
  };
};

export type Recruiter = {
  id: string;
  name: string;
  company: string;
  focus_area: string;
  relationship_stage: string;
  response_status: string;
  followup_due: string;
  quality_score: number;
};

export type DiscoveryResult = {
  discovered: number;
  saved: number;
  skipped: number;
  sources: string[];
  jobs: Job[];
  message: string;
};

export type DraftResult = {
  subject: string;
  body: string;
  channel?: string;
  requires_approval: boolean;
  download_url?: string;
};

export type ResumeArtifact = {
  pdf_filename: string;
  pdf_generated: boolean;
  storage_path?: string;
  pdf_storage_path?: string;
  download_url?: string;
  compile_error?: string;
  storage_warning?: string;
};

export type ResumeCompilerStatus = {
  pdf_compiler: string;
  available: boolean;
  path?: string;
  template: string;
  output_directory: string;
  storage_bucket: string;
  message: string;
};

export type SkillGapResult = {
  matched_skills: string[];
  missing_skills: string[];
  recommended_learning: string[];
  positioning: string;
};

export type GithubProjectEvidence = {
  repo: string;
  url: string;
  summary: string;
  skills: string[];
};

export type InterviewPrepResult = {
  company_briefing: string;
  recommended_project: {
    name: string;
    why: string;
    learn_next: string[];
  };
  hr_round: Array<{
    question: string;
    answer: string;
  }>;
  technical_round: Array<{
    question: string;
    answer: string;
  }>;
  technical_round_2_advanced: Array<{
    question: string;
    answer: string;
  }>;
  final_hr_round: Array<{
    question: string;
    answer: string;
  }>;
  github_project_focus: GithubProjectEvidence[];
  talking_points: string[];
  focus_topics: string[];
  readme_context_note?: string;
};

export type CareerTargetingStrategy = {
  source: string;
  headline: string;
  top_roles: Array<{
    role: string;
    category: string;
    match: number;
    salary: string;
    missing: string[];
    growth: string;
    visa: string;
  }>;
  company_tiers: Record<string, string[]>;
  next_actions: string[];
  fastest_path_120k: string;
  best_learning_companies: string[];
  current_best_job: string;
};
