from app.models.digest import DigestPreview
from app.models.job import Job


def build_digest(period: str, jobs: list[Job]) -> DigestPreview:
    top_jobs = sorted(jobs, key=lambda job: job.score, reverse=True)[:5]
    label = "Test" if period == "test" else "Morning" if period == "morning" else "Evening"
    items = "".join(
        f"<li><strong>{job.title}</strong> at {job.company} - score {job.score}/100</li>" for job in top_jobs
    )
    html = f"""
    <h2>{label} Career Intelligence Digest</h2>
    <h3>Top jobs</h3>
    <ul>{items or "<li>No new jobs yet.</li>"}</ul>
    <h3>Recommended actions</h3>
    <ul>
      <li>Apply first to BESS, NEM, forecasting, and trading roles scoring 85+.</li>
      <li>Review recruiter follow-ups due today before sending any outreach.</li>
      <li>Generate tailored resume drafts only for roles you intend to apply to.</li>
    </ul>
    """
    text_items = "\n".join(f"- {job.title} at {job.company}: {job.score}/100" for job in top_jobs) or "- No new jobs yet."
    return DigestPreview(
        subject=f"{label} Career Intelligence Digest",
        html=html,
        text=(
            f"{label} Career Intelligence Digest\n\n"
            f"Top jobs\n{text_items}\n\n"
            "Recommended actions\n"
            "- Apply first to BESS, NEM, forecasting, and trading roles scoring 85+.\n"
            "- Review recruiter follow-ups due today before sending any outreach.\n"
            "- Generate tailored resume drafts only for roles you intend to apply to."
        ),
        top_jobs=top_jobs,
        recruiter_actions=["Review due follow-ups", "Draft outreach for high-fit roles"],
        recommendations=["Prioritise high NEM/BESS fit", "Keep every resume claim evidence-backed"],
    )
