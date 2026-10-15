from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class JobSource(StrEnum):
    seek = "seek"
    indeed = "indeed"
    gradconnection = "gradconnection"
    prosple = "prosple"
    ethicaljobs = "ethicaljobs"
    company = "company"
    gmail = "gmail"
    manual_linkedin = "manual_linkedin"
    manual = "manual"
    adzuna = "adzuna"
    career_nest = "career_nest"
    arbeitnow = "arbeitnow"


class JobStatus(StrEnum):
    new = "new"
    saved = "saved"
    ignored = "ignored"
    applied = "applied"
    interviewing = "interviewing"
    closed = "closed"


class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = "Australia"
    source: JobSource = JobSource.manual
    url: HttpUrl | None = None
    description: str = ""
    salary_min: int | None = None
    salary_max: int | None = None
    posted_at: date | None = None


class Job(JobCreate):
    id: str
    status: JobStatus = JobStatus.new
    score: int = 0
    score_breakdown: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class JobStatusUpdate(BaseModel):
    status: JobStatus


class JobRecommendation(BaseModel):
    job_score: int = Field(ge=0, le=100)
    interview_probability: int = Field(ge=0, le=100)
    recommended_action: str
    resume_strategy: str
    best_project_to_highlight: str
    reasons: list[str]
    missing_keywords: list[str]
    salary_estimate: str = ""


class JobDiscoveryResult(BaseModel):
    discovered: int
    saved: int
    skipped: int
    sources: list[str]
    jobs: list[Job]
    message: str


class SkillGapRequest(BaseModel):
    skills: list[str] = Field(default_factory=list)


class SkillGapResult(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    recommended_learning: list[str]
    positioning: str
