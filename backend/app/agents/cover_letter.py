from app.models.job import Job


def draft_cover_note(job: Job) -> dict:
    body = (
        f"Dear hiring team, I am excited to apply for the {job.title} role at {job.company}. "
        "My background is focused on Energy Market Analytics, with project work across AEMO NEM data, "
        "BESS trading analytics, electricity forecasting, SQL/Python workflows, and Power BI dashboards. "
        "I am particularly interested in roles where market insight, modelling, and clear decision support "
        "help improve renewable integration and energy operations. I would welcome the opportunity to discuss "
        "how my project experience can contribute to your team."
    )
    return {"subject": f"Application: {job.title}", "body": body[:850], "requires_approval": True}


def cover_note_filename(job: Job) -> str:
    safe_company = "".join(char if char.isalnum() else "_" for char in job.company).strip("_")
    safe_role = "".join(char if char.isalnum() else "_" for char in job.title).strip("_")
    return f"Vivek_Aryasomayajula_{safe_company}_{safe_role}_Cover_Letter.txt"
