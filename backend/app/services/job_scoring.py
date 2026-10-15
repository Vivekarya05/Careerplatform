import re

from app.models.job import JobCreate, JobRecommendation


PROFILE_KEYWORDS = {
    "energy": ["nem", "aemo", "electricity", "energy market", "renewable", "dispatch", "fcas", "utility", "utilities", "retailer", "network", "generator"],
    "business_energy": ["business analyst", "market systems", "trading systems", "utilities transformation", "energy software", "metering", "stakeholder", "requirements", "process improvement", "crm", "erp"],
    "bess": ["bess", "battery", "storage", "grid-scale", "arbitrage"],
    "forecasting": ["forecast", "xgboost", "lstm", "arima", "demand", "price forecasting"],
    "trading": ["trading", "spot price", "market operations", "dispatch pricing", "volatility", "trading systems"],
    "sql_python": ["python", "sql", "postgresql", "pandas", "power bi", "dax"],
    "consulting": ["consulting", "advisory", "modelling", "plexos", "market modelling"],
    "asset_der": ["der", "distributed energy", "asset management", "asset performance", "regulatory", "market systems", "metering"],
}

PROJECT_MAP = {
    "bess": "NEM Market Intelligence & BESS Trading Platform",
    "forecasting": "Electricity Demand Forecasting (ARIMA/XGBoost/LSTM)",
    "trading": "Electricity Price Forecasting & Market Behaviour",
    "sql_python": "PostgreSQL + Power BI energy analytics dashboard",
    "business_energy": "AEMO NEMWeb ETL Pipeline",
    "asset_der": "Network Constraints & Price Divergence Analytics",
    "energy": "AEMO NEMWeb ETL Pipeline",
}


def _hits(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    total = 0
    for keyword in keywords:
        cleaned = keyword.lower()
        if len(cleaned) <= 3:
            total += 1 if re.search(rf"\b{re.escape(cleaned)}\b", lowered) else 0
        else:
            total += 1 if cleaned in lowered else 0
    return total


def _salary_estimate(job: JobCreate, text: str) -> str:
    if job.salary_min and job.salary_max:
        currency = "INR" if "india" in text else "AUD"
        if currency == "INR":
            return f"Indicative listed range: ₹{round(job.salary_min / 100000, 1)}-{round(job.salary_max / 100000, 1)} LPA"
        return f"Listed range: ${job.salary_min:,}-${job.salary_max:,} AUD"

    is_india = any(term in text for term in ["india", "hyderabad", "bangalore", "bengaluru", "chennai", "mumbai"])
    is_senior = any(term in text for term in ["senior", "lead", "principal", "manager"])
    is_grad = any(term in text for term in ["graduate", "junior", "entry level", "associate"])
    is_premium = any(term in text for term in ["bess", "battery", "trading", "modelling", "forecast", "market operations", "plexos"])
    is_energy_ba = "business analyst" in text and any(term in text for term in ["energy", "utilities", "utility", "market systems", "trading systems", "metering"])

    if is_india:
        if is_senior:
            return "Expected range: ₹25-45 LPA"
        if is_grad:
            return "Expected range: ₹7-14 LPA"
        return "Expected range: ₹12-28 LPA"

    if is_senior:
        return "Expected range: $140k-$190k AUD"
    if is_grad:
        return "Expected range: $75k-$95k AUD"
    if is_premium or is_energy_ba:
        return "Expected range: $110k-$155k AUD"
    return "Expected range: $90k-$125k AUD"


def score_job(job: JobCreate) -> JobRecommendation:
    text = " ".join([job.title, job.company, job.location or "", job.description or ""]).lower()
    component_scores: dict[str, int] = {}
    for category, keywords in PROFILE_KEYWORDS.items():
        matches = _hits(text, keywords)
        component_scores[category] = min(100, matches * 25)

    seniority_fit = 95
    if any(term in text for term in ["senior", "lead", "principal", "manager"]):
        seniority_fit = 62
    if any(term in text for term in ["graduate", "junior", "analyst", "associate"]):
        seniority_fit = 92

    visa_suitability = 70
    if any(term in text for term in ["citizen", "security clearance", "nv1"]):
        visa_suitability = 35
    if any(term in text for term in ["visa", "sponsorship", "graduate program"]):
        visa_suitability = 82

    weighted = (
        component_scores["energy"] * 0.20
        + component_scores["business_energy"] * 0.16
        + component_scores["bess"] * 0.18
        + component_scores["forecasting"] * 0.12
        + component_scores["trading"] * 0.13
        + component_scores["sql_python"] * 0.13
        + component_scores["consulting"] * 0.04
        + component_scores["asset_der"] * 0.06
        + seniority_fit * 0.04
        + visa_suitability * 0.04
    )
    strategic_bonus = min(
        21,
        sum(
            3
            for keyword in ["aemo", "nem", "bess", "battery", "fcas", "forecasting", "trading", "plexos", "utilities", "market systems", "der", "metering"]
            if keyword in text
        ),
    )
    role_combo_bonus = 0
    if component_scores["energy"] >= 50 and component_scores["bess"] >= 25:
        role_combo_bonus += 10
    if component_scores["trading"] >= 25 and any(term in text for term in ["dispatch", "spot price", "fcas", "volatility"]):
        role_combo_bonus += 8
    if component_scores["forecasting"] >= 25 and component_scores["sql_python"] >= 25:
        role_combo_bonus += 8
    if any(term in text for term in ["aemo", "nem", "fcas"]) and any(term in text for term in ["python", "sql", "power bi", "forecast", "trading"]):
        role_combo_bonus += 7
    if "business analyst" in text and any(term in text for term in ["energy", "utilities", "utility", "market systems", "trading systems", "metering", "der"]):
        role_combo_bonus += 14
    if component_scores["business_energy"] >= 50 and component_scores["sql_python"] >= 25:
        role_combo_bonus += 8

    job_score = max(0, min(100, round(weighted + strategic_bonus + role_combo_bonus)))
    strongest = max(component_scores, key=component_scores.get)
    if any(term in text for term in ["bess", "battery", "storage"]):
        strongest = "bess"
    elif any(term in text for term in ["forecast", "demand"]):
        strongest = "forecasting"
    elif any(term in text for term in ["trading", "dispatch pricing", "spot price"]):
        strongest = "trading"
    elif any(term in text for term in ["business analyst", "market systems", "trading systems", "metering"]):
        strongest = "business_energy"
    elif any(term in text for term in ["der", "asset performance", "asset management", "regulatory"]):
        strongest = "asset_der"
    missing_keywords = [
        keyword
        for keyword in ["Energy markets", "Utilities", "BESS", "AEMO", "FCAS", "PLEXOS", "Power BI", "Python", "SQL", "forecasting", "Market systems", "DER"]
        if keyword.lower() not in text
    ]
    action = "Apply this week"
    if job_score >= 88:
        action = "Prioritise today"
    elif job_score < 55:
        action = "Monitor or ignore unless strategically useful"

    return JobRecommendation(
        job_score=job_score,
        interview_probability=max(10, min(90, round(job_score * 0.72))),
        recommended_action=action,
        resume_strategy="Position as Business Analyst in Energy: lead with utilities/process analytics, NEM/AEMO data, SQL/Python, Power BI, market systems and project-backed evidence.",
        best_project_to_highlight=PROJECT_MAP.get(strongest, "NEM Market Intelligence & BESS Trading Platform"),
        reasons=[
            f"Energy fit {component_scores['energy']}/100",
            f"Business analyst in energy fit {component_scores['business_energy']}/100",
            f"BESS fit {component_scores['bess']}/100",
            f"Forecasting fit {component_scores['forecasting']}/100",
            f"Trading fit {component_scores['trading']}/100",
            f"SQL/Python fit {component_scores['sql_python']}/100",
            f"DER/asset/market systems fit {component_scores['asset_der']}/100",
        ],
        missing_keywords=missing_keywords[:8],
        salary_estimate=_salary_estimate(job, text),
    )
