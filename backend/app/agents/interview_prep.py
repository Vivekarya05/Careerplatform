from app.core.config import settings
from app.models.job import Job
from app.services.github_profile import fetch_github_project_evidence
from app.services.openai_service import OpenAIService


TOPICS = ["NEM", "AEMO", "FCAS", "BESS", "Forecasting", "Negative pricing", "Interconnectors", "Power BI", "SQL", "Python"]

PROJECT_EVIDENCE = {
    "bess": {
        "name": "NEM Market Intelligence & BESS Trading Platform",
        "why": "Best evidence for dispatch pricing, BESS arbitrage, NEM market behaviour, and trading analytics.",
        "learn_next": ["BESS bidding constraints", "FCAS co-optimisation", "Revenue stacking and degradation assumptions"],
    },
    "forecasting": {
        "name": "Electricity Demand Forecasting (ARIMA/XGBoost/LSTM)",
        "why": "Best evidence for time-series modelling, validation, feature engineering, and forecast explainability.",
        "learn_next": ["Forecast backtesting", "Peak demand drivers", "Weather and calendar feature engineering"],
    },
    "trading": {
        "name": "Electricity Price Forecasting & Market Behaviour",
        "why": "Best evidence for volatility, negative pricing, price spikes, and market operations thinking.",
        "learn_next": ["Price cap/floor behaviour", "Interconnector impacts", "Renewable intermittency and rebidding context"],
    },
    "data": {
        "name": "AEMO NEMWeb ETL Pipeline",
        "why": "Best evidence for reliable market data ingestion, validation, PostgreSQL modelling, and analytics foundations.",
        "learn_next": ["MMS table relationships", "Data quality checks", "Incremental load and monitoring patterns"],
    },
    "bi": {
        "name": "PostgreSQL + Power BI energy analytics dashboard",
        "why": "Best evidence for stakeholder-ready Power BI, SQL, DAX, and market reporting.",
        "learn_next": ["DAX time intelligence", "Drill-through pages", "Executive KPI design for market operations"],
    },
}


def _primary_project(job: Job) -> dict:
    text = f"{job.title} {job.description} {job.score_breakdown}".lower()
    if any(term in text for term in ["bess", "battery", "storage"]):
        return PROJECT_EVIDENCE["bess"]
    if any(term in text for term in ["forecast", "demand", "xgboost", "lstm"]):
        return PROJECT_EVIDENCE["forecasting"]
    if any(term in text for term in ["trading", "price", "dispatch", "volatility", "negative pricing"]):
        return PROJECT_EVIDENCE["trading"]
    if any(term in text for term in ["power bi", "dax", "dashboard"]):
        return PROJECT_EVIDENCE["bi"]
    return PROJECT_EVIDENCE["data"]


def _qa(question: str, answer: str) -> dict[str, str]:
    return {"question": question, "answer": answer}


def _fallback_brief(job: Job, github_projects: list[dict]) -> dict:
    project = _primary_project(job)
    repo_note = (
        f"Read {len(github_projects)} GitHub README project(s). Use the strongest matching project evidence below."
        if github_projects
        else "GitHub README context was unavailable, so this uses configured project evidence."
    )
    return {
        "company_briefing": f"Prepare a concise view on {job.company}, the role's likely NEM/BESS/forecasting exposure, and how your Python, SQL, Power BI and AEMO project evidence fits.",
        "recommended_project": project,
        "hr_round": [
            _qa("Walk me through your background.", "Position yourself as an energy analytics candidate who combines business analysis, energy systems experience, and hands-on NEM data projects. Keep the answer under 90 seconds and end with why this role is the logical next step."),
            _qa("Why this company and role?", f"Connect {job.company} to the Australian energy transition, market operations, forecasting or BESS work. Then point to your NEM data pipeline and forecasting projects as evidence."),
            _qa("Tell me about a time you handled messy data.", "Use the AEMO/NEMWeb ETL project: fragmented source files, validation checks, SQL/PostgreSQL structure, then Power BI or notebook analysis for market insight."),
        ],
        "technical_round": [
            _qa("How would you explain five-minute dispatch pricing?", "The dispatch price reflects the marginal cost of balancing supply and demand every five minutes, shaped by bids, constraints, outages, interconnectors and renewable output. Show how you would validate it using AEMO data."),
            _qa("What would you validate before trusting a demand or price forecast?", "Check timestamp alignment, missing intervals, leakage, weather/calendar features, regional error, peak performance, and benchmark models before adding XGBoost/LSTM complexity."),
            _qa("How would Power BI help this role?", "Use Power BI for operational dashboards: price volatility, demand, renewable output, BESS windows, exception monitoring and stakeholder-ready drill-downs."),
        ],
        "technical_round_2_advanced": [
            _qa("How can BESS assets create value in volatile NEM markets?", "Discuss arbitrage, FCAS, constraints, state of charge, degradation, bidding strategy and dispatch risk rather than just charge-low/discharge-high."),
            _qa("How would you analyse negative pricing?", "Connect rooftop solar, wind/solar output, demand, constraints, bidding behaviour and interconnector flows. Then propose AEMO data tables and features to inspect."),
            _qa("How would you build a robust market intelligence pipeline?", "Use incremental ingestion, schema validation, duplicate checks, quality flags, PostgreSQL models, scheduled refreshes, observability and BI outputs."),
        ],
        "final_hr_round": [
            _qa("What are your salary expectations?", "Give a researched range, stay flexible, and anchor to role scope: 'For a graduate to early energy analytics role in Sydney, I am targeting market-aligned compensation and prioritising the right NEM/BESS learning path.'"),
            _qa("Do you need sponsorship?", "Be factual and calm about your 485/visa pathway, then return to value: Python/SQL, AEMO data, Power BI, forecasting and energy systems background."),
            _qa("When can you start?", "Give a clear start window and mention you can prepare before joining by reviewing public market reports, AEMO docs and the company's portfolio."),
        ],
        "github_project_focus": github_projects[:5],
        "talking_points": [
            "AEMO dispatch pricing creates operational and trading signals",
            "BESS revenue depends on volatility, FCAS, constraints and state-of-charge discipline",
            "Negative pricing links to renewable output, demand, constraints and bidding behaviour",
            "Forecasting must be benchmarked, explainable and backtested",
            "Power BI should support operational decisions, not only reporting",
        ],
        "focus_topics": TOPICS,
        "readme_context_note": repo_note,
    }


async def _ai_brief(job: Job, fallback: dict) -> dict:
    if not settings.openai_api_key:
        return fallback
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "company_briefing": {"type": "string"},
            "recommended_project": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "why": {"type": "string"},
                    "learn_next": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "why", "learn_next"],
            },
            "hr_round": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"question": {"type": "string"}, "answer": {"type": "string"}}, "required": ["question", "answer"]}},
            "technical_round": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"question": {"type": "string"}, "answer": {"type": "string"}}, "required": ["question", "answer"]}},
            "technical_round_2_advanced": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"question": {"type": "string"}, "answer": {"type": "string"}}, "required": ["question", "answer"]}},
            "final_hr_round": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"question": {"type": "string"}, "answer": {"type": "string"}}, "required": ["question", "answer"]}},
            "github_project_focus": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"repo": {"type": "string"}, "url": {"type": "string"}, "summary": {"type": "string"}, "skills": {"type": "array", "items": {"type": "string"}}}, "required": ["repo", "url", "summary", "skills"]}},
            "talking_points": {"type": "array", "items": {"type": "string"}},
            "focus_topics": {"type": "array", "items": {"type": "string"}},
            "readme_context_note": {"type": "string"},
        },
        "required": [
            "company_briefing",
            "recommended_project",
            "hr_round",
            "technical_round",
            "technical_round_2_advanced",
            "final_hr_round",
            "github_project_focus",
            "talking_points",
            "focus_topics",
            "readme_context_note",
        ],
    }
    try:
        return await OpenAIService().structured_json(
            system=(
                "You are a senior Australian energy industry hiring manager. Build interview prep for Vivek. "
                "Use only the supplied job and project evidence. Be practical, Australian, concise, and specific to NEM, AEMO, BESS, forecasting, Power BI, SQL and Python. Return JSON only."
            ),
            user=f"Job: {job.model_dump(mode='json')}\nFallback/project evidence: {fallback}",
            schema_name="interview_prep_engine",
            schema=schema,
        )
    except Exception:
        return fallback


async def generate_interview_brief(job: Job) -> dict:
    github_projects = [project.__dict__ for project in await fetch_github_project_evidence()]
    fallback = _fallback_brief(job, github_projects)
    return await _ai_brief(job, fallback)
