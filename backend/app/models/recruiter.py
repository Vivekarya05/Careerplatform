from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, HttpUrl


class RelationshipStage(StrEnum):
    new = "new"
    reached_out = "reached_out"
    replied = "replied"
    call_scheduled = "call_scheduled"
    interview = "interview"
    opportunity_active = "opportunity_active"
    closed = "closed"


class Recruiter(BaseModel):
    id: str
    name: str
    email: EmailStr | None = None
    company: str | None = None
    linkedin: HttpUrl | None = None
    focus_area: str | None = None
    relationship_stage: RelationshipStage = RelationshipStage.new
    response_status: str | None = None
    last_contact: date | None = None
    followup_due: date | None = None
    quality_score: int = 50
    created_at: datetime
    updated_at: datetime

