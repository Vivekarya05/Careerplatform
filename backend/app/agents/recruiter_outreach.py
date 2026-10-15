from app.models.job import Job
from app.models.recruiter import Recruiter


TEMPLATE_TYPES = [
    "cold_outreach",
    "warm_outreach",
    "post_application",
    "networking",
    "follow_up",
    "referral_ask",
    "thank_you",
    "hiring_manager_outreach",
]


def draft_outreach(template_type: str, recruiter: Recruiter, job: Job | None = None) -> str:
    company = recruiter.company or (job.company if job else "your team")
    role = job.title if job else "energy analytics opportunities"
    return (
        f"Hi {recruiter.name},\n\n"
        f"I am Vivek Bharadwaj Aryasomayajula, an Energy Market Analytics candidate in Sydney "
        f"with Python, SQL, Power BI, NEM data, forecasting, and BESS analytics project experience. "
        f"I noticed {company}'s work around {role} and would value a short conversation if my profile "
        f"could be relevant.\n\n"
        "Thanks,\nVivek"
    )

