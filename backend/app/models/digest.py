from pydantic import BaseModel

from app.models.job import Job


class DigestRequest(BaseModel):
    period: str = "morning"
    send: bool = False


class DigestPreview(BaseModel):
    subject: str
    html: str
    text: str
    top_jobs: list[Job]
    recruiter_actions: list[str]
    recommendations: list[str]
