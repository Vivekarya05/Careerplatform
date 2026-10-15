from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse, PlainTextResponse

from app.core.security import require_authenticated_user
from app.agents.job_discovery import discover_jobs, is_target_australian_energy_job
from app.agents.skill_gap import build_skill_gap
from app.agents.ats_scoring import score_resume
from app.agents.career_strategy import today_strategy
from app.agents.career_targeting import build_targeting_strategy
from app.agents.cover_letter import cover_note_filename, draft_cover_note
from app.agents.interview_prep import generate_interview_brief
from app.agents.market_intelligence import weekly_market_report
from app.agents.recruiter_outreach import draft_outreach
from app.agents.resume_generator import draft_resume_strategy
from app.models.digest import DigestPreview, DigestRequest
from app.models.job import Job, JobCreate, JobDiscoveryResult, JobStatus, JobStatusUpdate, SkillGapRequest, SkillGapResult
from app.models.recruiter import Recruiter
from app.services.digest_service import build_digest
from app.services.email_service import EmailService
from app.services import job_store
from app.services.github_profile import infer_github_skills
from app.services.outreach_service import OutreachRequest, draft_outreach_for_job
from app.services.resume_service import build_resume_artifact, save_resume_version
from app.services.resume_service import compiler_status

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/jobs", response_model=Job)
async def create_job(payload: JobCreate, user_id: str = Depends(require_authenticated_user)) -> Job:
    return await job_store.create_job(user_id, payload)


@router.get("/jobs", response_model=list[Job])
async def list_jobs(user_id: str = Depends(require_authenticated_user)) -> list[Job]:
    return [
        job
        for job in await job_store.list_jobs(user_id)
        if is_target_australian_energy_job(JobCreate(**job.model_dump()), ["Australia"])
    ]


@router.post("/jobs/cleanup/non-target")
async def cleanup_non_target_jobs(user_id: str = Depends(require_authenticated_user)) -> dict:
    all_jobs = await job_store.list_jobs(user_id)
    non_target = [
        job
        for job in all_jobs
        if not is_target_australian_energy_job(JobCreate(**job.model_dump()), ["Australia"])
    ]
    ignored = await job_store.ignore_jobs(user_id, non_target)
    return {
        "ignored": ignored,
        "message": f"Ignored {ignored} non-Australian or non-target saved jobs.",
    }


@router.post("/jobs/discover", response_model=JobDiscoveryResult)
async def discover_and_save_jobs(
    countries: str | None = Query(default=None),
    user_id: str = Depends(require_authenticated_user),
) -> JobDiscoveryResult:
    country_list = [country.strip() for country in countries.split(",") if country.strip()] if countries else ["Australia"]
    discovered = await discover_jobs(country_list)
    saved_jobs: list[Job] = []
    skipped = 0
    for payload in discovered:
        saved = await job_store.create_job_if_new(user_id, payload)
        if saved:
            saved_jobs.append(saved)
        else:
            skipped += 1
    all_jobs = [
        job
        for job in await job_store.list_jobs(user_id)
        if is_target_australian_energy_job(JobCreate(**job.model_dump()), country_list)
    ]
    sources = sorted({job.source.value if hasattr(job.source, "value") else str(job.source) for job in discovered})
    if not discovered:
        selected = ", ".join(country_list or ["Australia"])
        message = f"No matching live jobs found for {selected}. Add Adzuna credentials for stronger Australia coverage."
    elif saved_jobs:
        message = f"Discovered {len(discovered)} live jobs and saved {len(saved_jobs)} new opportunities."
    else:
        message = f"Discovery ran live. {skipped} matching jobs were already saved."
    return JobDiscoveryResult(
        discovered=len(discovered),
        saved=len(saved_jobs),
        skipped=skipped,
        sources=sources,
        jobs=all_jobs,
        message=message,
    )


@router.post("/jobs/{job_id}/score")
async def score_existing_job(job_id: str, user_id: str = Depends(require_authenticated_user)) -> dict:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return await job_store.rescore_job(user_id, job)


@router.patch("/jobs/{job_id}/status", response_model=Job)
async def update_job_status(
    job_id: str, payload: JobStatusUpdate, user_id: str = Depends(require_authenticated_user)
) -> Job:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return await job_store.update_status(user_id, job, payload.status)


@router.post("/digests", response_model=DigestPreview)
async def digest(payload: DigestRequest, user_id: str = Depends(require_authenticated_user)) -> DigestPreview:
    jobs = [
        job
        for job in await job_store.list_jobs(user_id)
        if is_target_australian_energy_job(JobCreate(**job.model_dump()), ["Australia"])
    ]
    preview = build_digest(payload.period, jobs)
    if payload.send:
        await EmailService().send_digest(preview)
    return preview


@router.get("/career/today")
async def career_today(user_id: str = Depends(require_authenticated_user)) -> dict:
    return today_strategy()


@router.get("/career/targeting-strategy")
async def career_targeting_strategy(user_id: str = Depends(require_authenticated_user)) -> dict:
    return await build_targeting_strategy(await job_store.list_jobs(user_id))


@router.get("/market-intelligence/weekly")
async def market_intelligence(user_id: str = Depends(require_authenticated_user)) -> dict:
    return weekly_market_report(await job_store.list_jobs(user_id))


@router.get("/jobs/{job_id}/interview-prep")
async def interview_prep(job_id: str, user_id: str = Depends(require_authenticated_user)) -> dict:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return await generate_interview_brief(job)


@router.get("/jobs/{job_id}/resume-strategy")
async def resume_strategy(job_id: str, user_id: str = Depends(require_authenticated_user)) -> dict:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return draft_resume_strategy(job)


@router.post("/jobs/{job_id}/resume")
async def generate_resume(job_id: str, user_id: str = Depends(require_authenticated_user)) -> dict:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not is_target_australian_energy_job(JobCreate(**job.model_dump()), ["Australia"]):
        await job_store.update_status(user_id, job, JobStatus.ignored)
        raise HTTPException(
            status_code=400,
            detail="This saved job is outside the Australian energy analytics target list, so resume generation was blocked and the job was ignored.",
        )
    artifact = build_resume_artifact(job)
    saved = save_resume_version(user_id, job, artifact)
    saved["download_url"] = f"/api/jobs/{job_id}/resume/download"
    return saved


@router.get("/resume/compiler")
async def resume_compiler(user_id: str = Depends(require_authenticated_user)) -> dict:
    return compiler_status()


@router.get("/jobs/{job_id}/resume/download")
async def download_resume(job_id: str, user_id: str = Depends(require_authenticated_user)):
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not is_target_australian_energy_job(JobCreate(**job.model_dump()), ["Australia"]):
        await job_store.update_status(user_id, job, JobStatus.ignored)
        raise HTTPException(
            status_code=400,
            detail="This saved job is outside the Australian energy analytics target list, so resume download was blocked and the job was ignored.",
        )
    artifact = build_resume_artifact(job)
    if artifact["pdf_generated"] and artifact["pdf_path"]:
        return FileResponse(
            artifact["pdf_path"],
            media_type="application/pdf",
            filename=artifact["pdf_filename"],
        )
    return PlainTextResponse(
        artifact["latex_source"],
        media_type="application/x-tex",
        headers={"Content-Disposition": f"attachment; filename={artifact['pdf_filename'].replace('.pdf', '.tex')}"},
    )


@router.get("/jobs/{job_id}/cover-note")
async def cover_note(job_id: str, user_id: str = Depends(require_authenticated_user)) -> dict:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    draft = draft_cover_note(job)
    draft["download_url"] = f"/api/jobs/{job_id}/cover-note/download"
    return draft


@router.get("/jobs/{job_id}/cover-note/download")
async def download_cover_note(job_id: str, user_id: str = Depends(require_authenticated_user)) -> Response:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    draft = draft_cover_note(job)
    content = f"{draft['subject']}\n\n{draft['body']}\n"
    return PlainTextResponse(
        content,
        headers={"Content-Disposition": f"attachment; filename={cover_note_filename(job)}"},
    )


@router.post("/jobs/{job_id}/skill-gap", response_model=SkillGapResult)
async def skill_gap(job_id: str, payload: SkillGapRequest, user_id: str = Depends(require_authenticated_user)) -> SkillGapResult:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return build_skill_gap(job, payload.skills)


@router.get("/profile/skills")
async def profile_skills(user_id: str = Depends(require_authenticated_user)) -> dict:
    return {"skills": await job_store.get_profile_skills(user_id)}


@router.put("/profile/skills")
async def save_profile_skills(payload: dict, user_id: str = Depends(require_authenticated_user)) -> dict:
    skills = payload.get("skills") or []
    if not isinstance(skills, list):
        raise HTTPException(status_code=400, detail="skills must be a list")
    return {"skills": await job_store.save_profile_skills(user_id, [str(skill) for skill in skills])}


@router.get("/profile/skills/github")
async def github_skills(user_id: str = Depends(require_authenticated_user)) -> dict:
    return await infer_github_skills()


@router.post("/jobs/{job_id}/outreach")
async def job_outreach(
    job_id: str, payload: OutreachRequest, user_id: str = Depends(require_authenticated_user)
) -> dict:
    job = await job_store.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return draft_outreach_for_job(job, payload)


@router.post("/ats-score")
async def ats_score(payload: dict, user_id: str = Depends(require_authenticated_user)) -> dict:
    return score_resume(payload.get("resume_text", ""), payload.get("job_description", ""))


@router.post("/recruiter-outreach")
async def recruiter_outreach(payload: dict, user_id: str = Depends(require_authenticated_user)) -> dict:
    now = datetime.now(timezone.utc)
    recruiter_payload = dict(payload["recruiter"])
    recruiter_payload.setdefault("id", str(uuid4()))
    recruiter_payload.setdefault("created_at", now)
    recruiter_payload.setdefault("updated_at", now)
    recruiter = Recruiter(
        **recruiter_payload,
    )
    job = await job_store.get_job(user_id, payload["job_id"]) if payload.get("job_id") else None
    body = draft_outreach(payload.get("template_type", "cold_outreach"), recruiter, job)
    return {"subject": "Energy analytics opportunity", "body": body, "requires_approval": True}
