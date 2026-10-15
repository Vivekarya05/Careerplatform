from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import settings
from app.core.supabase_client import get_supabase
from app.models.job import Job, JobCreate, JobStatus
from app.services.job_scoring import score_job

_memory_jobs: dict[str, Job] = {}
_memory_skills: dict[str, list[str]] = {}
_runtime_memory_store = False


def _use_memory_store() -> bool:
    return _runtime_memory_store or not settings.supabase_url or not settings.supabase_service_role_key


def _enable_runtime_memory_store() -> None:
    global _runtime_memory_store
    _runtime_memory_store = True


def _job_from_row(row: dict) -> Job:
    return Job(
        id=row["id"],
        title=row["title"],
        company=row["company"],
        location=row.get("location"),
        source=row["source"],
        url=row.get("url"),
        description=row.get("description") or "",
        salary_min=row.get("salary_min"),
        salary_max=row.get("salary_max"),
        posted_at=row.get("posted_at"),
        status=row.get("status", JobStatus.new),
        score=row.get("score", 0),
        score_breakdown=row.get("score_breakdown") or {},
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _job_insert(user_id: str, payload: JobCreate, score: int, score_breakdown: dict) -> dict:
    data = payload.model_dump(mode="json")
    data.update(
        {
            "user_id": user_id,
            "score": score,
            "score_breakdown": score_breakdown,
        }
    )
    return data


async def create_job(user_id: str, payload: JobCreate) -> Job:
    recommendation = score_job(payload)
    now = datetime.now(timezone.utc)
    if _use_memory_store():
        return _create_memory_job(payload, recommendation.model_dump(), recommendation.job_score, now)

    try:
        response = (
            get_supabase()
            .table("jobs")
            .insert(_job_insert(user_id, payload, recommendation.job_score, recommendation.model_dump()))
            .execute()
        )
        return _job_from_row(response.data[0])
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            return _create_memory_job(payload, recommendation.model_dump(), recommendation.job_score, now)
        raise


def _create_memory_job(payload: JobCreate, score_breakdown: dict, score: int, now: datetime) -> Job:
    job = Job(
        **payload.model_dump(),
        id=str(uuid4()),
        status=JobStatus.new,
        score=score,
        score_breakdown=score_breakdown,
        created_at=now,
        updated_at=now,
    )
    _memory_jobs[job.id] = job
    return job


async def create_job_if_new(user_id: str, payload: JobCreate) -> Job | None:
    existing = await find_duplicate_job(user_id, payload)
    if existing:
        return None
    try:
        return await create_job(user_id, payload)
    except Exception as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
            return None
        raise


async def list_jobs(user_id: str) -> list[Job]:
    if _use_memory_store():
        return sorted(_memory_jobs.values(), key=lambda job: job.score, reverse=True)
    try:
        response = (
            get_supabase()
            .table("jobs")
            .select("*")
            .eq("user_id", user_id)
            .order("score", desc=True)
            .execute()
        )
        return [_job_from_row(row) for row in response.data]
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            return sorted(_memory_jobs.values(), key=lambda job: job.score, reverse=True)
        raise


async def get_job(user_id: str, job_id: str) -> Job | None:
    if _use_memory_store():
        return _memory_jobs.get(job_id)
    try:
        response = (
            get_supabase()
            .table("jobs")
            .select("*")
            .eq("user_id", user_id)
            .eq("id", job_id)
            .limit(1)
            .execute()
        )
        return _job_from_row(response.data[0]) if response.data else None
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            return _memory_jobs.get(job_id)
        raise


async def find_duplicate_job(user_id: str, payload: JobCreate) -> Job | None:
    if _use_memory_store():
        for job in _memory_jobs.values():
            same_owner = True
            same_url = bool(payload.url and job.url and str(payload.url) == str(job.url))
            same_title_company = (
                job.title.strip().lower() == payload.title.strip().lower()
                and job.company.strip().lower() == payload.company.strip().lower()
            )
            if same_owner and (same_url or same_title_company):
                return job
        return None

    try:
        query = (
            get_supabase()
            .table("jobs")
            .select("*")
            .eq("user_id", user_id)
            .eq("title", payload.title)
            .eq("company", payload.company)
            .limit(1)
        )
        response = query.execute()
        if response.data:
            return _job_from_row(response.data[0])
        if payload.url:
            response = (
                get_supabase()
                .table("jobs")
                .select("*")
                .eq("user_id", user_id)
                .eq("url", str(payload.url))
                .limit(1)
                .execute()
            )
            if response.data:
                return _job_from_row(response.data[0])
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            return await find_duplicate_job(user_id, payload)
        raise
    return None


async def rescore_job(user_id: str, job: Job) -> dict:
    recommendation = score_job(JobCreate(**job.model_dump()))
    job.score = recommendation.job_score
    job.score_breakdown = recommendation.model_dump()
    job.updated_at = datetime.now(timezone.utc)
    if _use_memory_store():
        _memory_jobs[job.id] = job
    else:
        (
            get_supabase()
            .table("jobs")
            .update(
                {
                    "score": recommendation.job_score,
                    "score_breakdown": recommendation.model_dump(),
                    "updated_at": job.updated_at.isoformat(),
                }
            )
            .eq("user_id", user_id)
            .eq("id", job.id)
            .execute()
        )
    return recommendation.model_dump()


async def update_status(user_id: str, job: Job, status: JobStatus) -> Job:
    job.status = status
    job.updated_at = datetime.now(timezone.utc)
    if _use_memory_store():
        _memory_jobs[job.id] = job
        return job
    try:
        response = (
            get_supabase()
            .table("jobs")
            .update({"status": status.value, "updated_at": job.updated_at.isoformat()})
            .eq("user_id", user_id)
            .eq("id", job.id)
            .execute()
        )
        return _job_from_row(response.data[0]) if response.data else job
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            _memory_jobs[job.id] = job
            return job
        raise


async def ignore_jobs(user_id: str, jobs: list[Job]) -> int:
    if not jobs:
        return 0
    now = datetime.now(timezone.utc)
    if _use_memory_store():
        for job in jobs:
            job.status = JobStatus.ignored
            job.updated_at = now
            _memory_jobs[job.id] = job
        return len(jobs)
    try:
        (
            get_supabase()
            .table("jobs")
            .update({"status": JobStatus.ignored.value, "updated_at": now.isoformat()})
            .eq("user_id", user_id)
            .in_("id", [job.id for job in jobs])
            .execute()
        )
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            return await ignore_jobs(user_id, jobs)
        raise
    return len(jobs)


async def get_profile_skills(user_id: str) -> list[str]:
    if _use_memory_store():
        return _memory_skills.get(user_id, [])
    try:
        response = (
            get_supabase()
            .table("profiles")
            .select("skills")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0].get("skills") or []
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            return _memory_skills.get(user_id, [])
        raise
    return []


async def save_profile_skills(user_id: str, skills: list[str]) -> list[str]:
    cleaned = sorted(dict.fromkeys(skill.strip() for skill in skills if skill.strip()))
    if _use_memory_store():
        _memory_skills[user_id] = cleaned
        return cleaned
    try:
        get_supabase().table("profiles").upsert(
            {
                "id": user_id,
                "full_name": "Vivek Bharadwaj Aryasomayajula",
                "location": "Sydney, Australia",
                "target_roles": [
                    "Business Analyst - Energy Markets",
                    "Business Analyst - Trading Systems",
                    "Business Analyst - Utilities",
                    "Market Systems Analyst",
                    "Operations Analyst - Energy",
                    "Commercial Analyst - Energy",
                    "Asset Performance Analyst",
                    "Energy Systems Analyst",
                    "Regulatory / Market Analyst",
                    "DER Analyst",
                    "Energy Market Analyst",
                    "Energy Market Modeller",
                    "BESS Analyst",
                    "Portfolio Analyst - Energy",
                    "Trading Analyst",
                    "Forecasting Analyst",
                    "Energy Data Analyst",
                ],
                "skills": cleaned,
            }
        ).execute()
    except Exception:
        if settings.public_access_enabled:
            _enable_runtime_memory_store()
            _memory_skills[user_id] = cleaned
            return cleaned
        raise
    return cleaned
