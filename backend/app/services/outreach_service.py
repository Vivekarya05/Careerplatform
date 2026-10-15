from typing import Literal

from pydantic import BaseModel

from app.models.job import Job

OutreachChannel = Literal["email", "linkedin_connection", "linkedin_dm"]
OutreachType = Literal[
    "cold_outreach",
    "warm_outreach",
    "post_application",
    "networking",
    "follow_up",
    "referral_ask",
    "thank_you",
    "hiring_manager_outreach",
]


class OutreachRequest(BaseModel):
    channel: OutreachChannel = "email"
    template_type: OutreachType = "cold_outreach"
    recipient_name: str | None = None
    recipient_role: str | None = None
    custom_context: str | None = None


def _name(value: str | None) -> str:
    return value.strip() if value else "there"


def _energy_hook(job: Job) -> str:
    text = f"{job.title} {job.company} {job.description}".lower()
    if any(term in text for term in ["bess", "battery", "storage"]):
        return "BESS trading analytics, NEM price signals, and storage optimisation"
    if any(term in text for term in ["forecast", "demand", "price"]):
        return "electricity forecasting, NEM data, and market behaviour analysis"
    if any(term in text for term in ["power bi", "dashboard", "sql"]):
        return "Power BI, SQL, PostgreSQL, and energy market reporting"
    return "Australian NEM analytics, AEMO data, forecasting, and renewable integration"


def draft_outreach_for_job(job: Job, request: OutreachRequest) -> dict:
    recipient = _name(request.recipient_name)
    role_context = f" ({request.recipient_role})" if request.recipient_role else ""
    hook = _energy_hook(job)
    context = f" {request.custom_context.strip()}" if request.custom_context else ""

    subject = f"Energy analytics interest - {job.title} at {job.company}"

    email_body = (
        f"Hi {recipient},\n\n"
        f"I hope you are well. I am Vivek Bharadwaj Aryasomayajula, an Energy Market Analytics candidate based in Sydney. "
        f"I came across the {job.title} role at {job.company} and was particularly interested because it aligns with my work across {hook}.\n\n"
        "My background includes Python, SQL, PostgreSQL, Power BI, AEMO NEM datasets, dispatch pricing, FCAS, forecasting, "
        "and BESS analytics projects. I would value the chance to briefly understand what the team is looking for and whether my profile could be relevant."
        f"{context}\n\n"
        "Thanks,\nVivek"
    )

    linkedin_connection = (
        f"Hi {recipient}, I am Vivek, an Energy Market Analytics candidate in Sydney. "
        f"I saw {job.company}'s {job.title} role and would value connecting around NEM, BESS, forecasting, and energy analytics opportunities."
    )

    linkedin_dm = (
        f"Hi {recipient}, thanks for connecting. I noticed the {job.title} role at {job.company} and it strongly aligns with my "
        f"Energy Market Analytics work across {hook}. I have project experience with Python, SQL, Power BI, AEMO NEM data, "
        "forecasting, dispatch pricing, FCAS, and BESS analytics. If useful, I would be grateful for a short conversation or any guidance on the best way to position my application."
    )

    if request.template_type == "post_application":
        email_body = (
            f"Hi {recipient},\n\n"
            f"I recently applied for the {job.title} role at {job.company}. I wanted to briefly introduce myself as a Sydney-based "
            f"Energy Market Analytics candidate with project experience across {hook}, plus Python, SQL, PostgreSQL, Power BI, and AEMO NEM data.\n\n"
            "I would appreciate any guidance on the hiring process or the team priorities for this role.\n\n"
            "Thanks,\nVivek"
        )
    elif request.template_type == "referral_ask":
        email_body = (
            f"Hi {recipient},\n\n"
            f"I am interested in the {job.title} role at {job.company}. My profile is focused on {hook}, with supporting skills in Python, SQL, "
            "Power BI, forecasting, AEMO data, and BESS analytics.\n\n"
            "If you feel my background is relevant, would you be comfortable pointing me to the right person or advising whether a referral is appropriate?\n\n"
            "Thanks,\nVivek"
        )
    elif request.template_type == "follow_up":
        subject = f"Following up - {job.title}"
        email_body = (
            f"Hi {recipient},\n\n"
            f"Just following up on my note about the {job.title} role at {job.company}. I remain very interested because of the fit with "
            f"{hook} and my Energy Market Analytics project background.\n\n"
            "Happy to send through a tailored resume or have a short conversation if helpful.\n\n"
            "Thanks,\nVivek"
        )

    body = email_body
    if request.channel == "linkedin_connection":
        subject = "LinkedIn connection note"
        body = linkedin_connection[:300]
    elif request.channel == "linkedin_dm":
        subject = "LinkedIn message"
        body = linkedin_dm

    return {
        "subject": subject,
        "body": body,
        "channel": request.channel,
        "template_type": request.template_type,
        "recipient": recipient,
        "recipient_role": role_context.strip(" ()") or None,
        "company": job.company,
        "job_title": job.title,
        "requires_approval": True,
        "send_policy": "draft_only_user_must_review",
    }

