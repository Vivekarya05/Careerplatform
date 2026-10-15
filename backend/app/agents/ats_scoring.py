REQUIRED_KEYWORDS = ["NEM", "AEMO", "BESS", "FCAS", "Python", "SQL", "Power BI", "forecasting", "dispatch pricing"]


def score_resume(resume_text: str, job_description: str) -> dict:
    combined = f"{resume_text}\n{job_description}".lower()
    missing = [keyword for keyword in REQUIRED_KEYWORDS if keyword.lower() not in combined]
    score = max(35, min(100, 100 - len(missing) * 7))
    return {
        "ats_score": score,
        "missing_keywords": missing,
        "project_emphasis": [
            "NEM Market Intelligence & BESS Trading Platform",
            "AEMO NEMWeb ETL Pipeline",
            "Electricity Demand Forecasting",
        ],
        "improvements": [
            "Mirror the job title language in the profile line.",
            "Show Python, SQL, and Power BI in project bullets where truthful.",
            "Add NEM/BESS/FCAS keywords only where backed by project evidence.",
        ],
    }

