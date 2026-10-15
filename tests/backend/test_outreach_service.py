from datetime import datetime, timezone

from app.models.job import Job, JobSource, JobStatus
from app.services.outreach_service import OutreachRequest, draft_outreach_for_job


def _job() -> Job:
    now = datetime.now(timezone.utc)
    return Job(
        id="job-1",
        title="BESS Trading Analyst",
        company="TagEnergy",
        location="Sydney",
        source=JobSource.manual,
        description="Battery storage trading analytics using NEM price signals and FCAS.",
        status=JobStatus.new,
        score=92,
        score_breakdown={},
        created_at=now,
        updated_at=now,
    )


def test_email_outreach_is_draft_only_and_job_specific() -> None:
    draft = draft_outreach_for_job(_job(), OutreachRequest(recipient_name="Sarah"))
    assert draft["requires_approval"] is True
    assert draft["send_policy"] == "draft_only_user_must_review"
    assert "BESS Trading Analyst" in draft["body"]
    assert "TagEnergy" in draft["body"]


def test_linkedin_connection_note_is_short() -> None:
    draft = draft_outreach_for_job(_job(), OutreachRequest(channel="linkedin_connection"))
    assert draft["channel"] == "linkedin_connection"
    assert len(draft["body"]) <= 300

