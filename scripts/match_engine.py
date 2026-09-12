"""
v1 skill-matching engine: keyword overlap between a job description and your
core skills. Simple and transparent by design — good enough to triage which
jobs are worth spending an AI call on. A natural v2 upgrade is embedding-based
semantic matching (e.g. sentence-transformers) once this basic version proves
the pipeline works end to end.
"""

# Broader vocabulary so we can detect skills the JD asks for that you DON'T
# have yet (the "gap" side of the comparison), not just the ones you do.
SKILL_VOCAB = [
    "SQL", "Python", "Power BI", "PostgreSQL", "MySQL", "Excel", "Tableau",
    "DAX", "JavaScript", "R", "SAS", "Java", "C#", "AWS", "Azure", "GCP",
    "Business Analysis", "Requirements Gathering", "Requirements Elicitation",
    "Stakeholder Management", "Process Improvement", "Agile", "Scrum",
    "Waterfall", "UAT", "BRD", "FRD", "Business Case", "User Stories",
    "Jira", "Confluence", "Visio", "BPMN", "UML",
    "CRM", "ERP", "SAP", "Salesforce", "Dynamics 365",
    "Data Analysis", "Data Visualization", "Data Governance", "ETL",
    "Machine Learning", "Forecasting", "Time Series",
    "AEMO", "NEM", "PLEXOS", "BESS", "Energy Market", "Renewable",
    "Dispatch Pricing", "Network Constraints", "FCAS",
]


def extract_skills(text: str, vocab: list[str] = SKILL_VOCAB) -> set[str]:
    text_lower = (text or "").lower()
    return {skill for skill in vocab if skill.lower() in text_lower}


def score_job(job_description: str, core_skills: list[str]) -> dict:
    jd_skills = extract_skills(job_description)
    my_skills = extract_skills(" ".join(core_skills))

    matched = sorted(jd_skills & my_skills)
    missing = sorted(jd_skills - my_skills)

    score = round(100 * len(matched) / len(jd_skills), 1) if jd_skills else 0.0

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }
