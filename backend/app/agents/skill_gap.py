from app.models.job import Job, SkillGapResult
from app.services.job_scoring import PROFILE_KEYWORDS


LEARNING_MAP = {
    "BESS": "Build one BESS arbitrage case study using 5-minute NEM prices and charge/discharge constraints.",
    "AEMO": "Add one AEMO NEMWeb data pipeline note showing source tables, validation, and dispatch interval handling.",
    "FCAS": "Create a short FCAS explainer with enablement, contingency services, and BESS participation examples.",
    "PLEXOS": "Document one PLEXOS Cloud scenario workflow and how outputs support market modelling decisions.",
    "Power BI": "Publish a Power BI dashboard page for price, demand, renewable generation, and volatility insights.",
    "Python": "Keep a clean Python notebook or repo module for forecasting, ETL, and market feature engineering.",
    "SQL": "Add SQL examples for dispatch price aggregation, regional demand, and renewable generation joins.",
    "forecasting": "Compare ARIMA, XGBoost, and LSTM forecast outputs with a clear validation metric table.",
}


def _normalise(skills: list[str]) -> set[str]:
    return {skill.strip().lower() for skill in skills if skill.strip()}


def build_skill_gap(job: Job, skills: list[str]) -> SkillGapResult:
    profile_skills = _normalise(skills)
    job_text = f"{job.title} {job.company} {job.description} {job.score_breakdown}".lower()
    required = set(job.score_breakdown.get("missing_keywords") or [])
    for keywords in PROFILE_KEYWORDS.values():
        for keyword in keywords:
            if keyword in job_text:
                required.add(keyword.upper() if len(keyword) <= 5 else keyword.title())

    matched = sorted(
        skill
        for skill in required
        if skill.lower() in profile_skills or any(skill.lower() in owned or owned in skill.lower() for owned in profile_skills)
    )
    missing = sorted(skill for skill in required if skill not in matched)
    recommended = [LEARNING_MAP.get(skill, f"Create evidence for {skill} with a small energy-market project.") for skill in missing[:6]]

    if missing:
        positioning = "Position your current NEM, forecasting, SQL/Python and Power BI evidence first, then close the gaps with targeted mini-projects."
    else:
        positioning = "This role is well aligned with your current skill profile. Tailor the resume around proof, project outcomes, and energy-market language."

    return SkillGapResult(
        matched_skills=matched[:12],
        missing_skills=missing[:12],
        recommended_learning=recommended,
        positioning=positioning,
    )
