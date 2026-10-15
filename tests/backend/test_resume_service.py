from datetime import datetime, timezone

from app.models.job import Job, JobSource, JobStatus
from app.services.resume_service import render_latex, resume_filename


def _job() -> Job:
    now = datetime.now(timezone.utc)
    return Job(
        id="job-1",
        title="BESS Trading Analyst",
        company="TagEnergy Australia",
        location="Sydney",
        source=JobSource.manual,
        description="BESS NEM trading analytics",
        status=JobStatus.new,
        score=92,
        score_breakdown={},
        created_at=now,
        updated_at=now,
    )


def test_resume_filename_uses_company_and_role() -> None:
    assert resume_filename(_job()) == "Vivek_Aryasomayajula_TagEnergy_Australia_BESS_Trading_Analyst_Resume.pdf"


def test_resume_template_renders_target_line() -> None:
    latex = render_latex(_job())
    assert "Target: BESS Trading Analyst at TagEnergy Australia" in latex
    assert "{{JOB_TITLE}}" not in latex
    assert "{{COMPANY}}" not in latex

