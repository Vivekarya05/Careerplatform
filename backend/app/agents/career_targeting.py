from app.models.job import Job
from app.services.openai_service import OpenAIService


PROFILE_SUMMARY = """
Vivek Bharadwaj Aryasomayajula is based in Sydney with a Master of Business Analytics,
B.Tech Power Engineering, ICT Business Analyst experience, energy/utilities project
engineering experience, finance/operations exposure, and current energy markets research
exposure. Core skills: Python, SQL, PostgreSQL, Power BI, ETL, dashboards, time-series
forecasting, AEMO/NEM data, dispatch price, demand analysis, renewable integration,
BESS, FCAS basics, electricity price/demand forecasting, GitHub project evidence.
Career goal: Business Analyst in Energy, Energy Market Analyst, Market Systems Analyst,
Energy Market Modeller, BESS Analyst, DER Analyst, Trading Systems Analyst, and Energy
Intelligence Professional in Australia. The strategic positioning is not Business
Analyst OR Energy; it is Business Analyst IN Energy across retailers, networks,
generators, renewable developers, BESS, energy software, metering, market systems,
trading systems, DER, asset management, and utilities transformation.
"""

TARGET_ROLES = [
    {"role": "Business Analyst - Energy Markets", "category": "Immediate fit", "match": 94, "salary": "$95k-$135k", "missing": ["Deeper market systems terminology", "Energy retailer operating model"], "growth": "Very high", "visa": "High"},
    {"role": "Business Analyst - Utilities", "category": "Immediate fit", "match": 93, "salary": "$90k-$130k", "missing": ["Australian utility transformation examples"], "growth": "High", "visa": "High"},
    {"role": "Business Analyst - Trading Systems", "category": "Immediate fit", "match": 90, "salary": "$105k-$150k", "missing": ["Trading lifecycle", "Risk/PnL workflow language"], "growth": "Very high", "visa": "Medium-high"},
    {"role": "Market Systems Analyst", "category": "Immediate fit", "match": 89, "salary": "$95k-$135k", "missing": ["Market systems support exposure", "NEM settlements basics"], "growth": "Very high", "visa": "Medium-high"},
    {"role": "Energy Market Analyst", "category": "Immediate fit", "match": 91, "salary": "$90k-$125k", "missing": ["Deeper FCAS", "NEMDE constraints"], "growth": "High", "visa": "Medium-high"},
    {"role": "Operations Analyst - Energy", "category": "Immediate fit", "match": 88, "salary": "$85k-$120k", "missing": ["Australian operations centre processes"], "growth": "High", "visa": "High"},
    {"role": "Energy Data Analyst", "category": "Immediate fit", "match": 90, "salary": "$85k-$120k", "missing": ["Production data engineering"], "growth": "High", "visa": "High"},
    {"role": "Power BI Analyst - Energy", "category": "Immediate fit", "match": 88, "salary": "$85k-$115k", "missing": ["Advanced DAX patterns"], "growth": "Medium-high", "visa": "High"},
    {"role": "Market Operations Analyst", "category": "Immediate fit", "match": 84, "salary": "$90k-$125k", "missing": ["Operational dispatch processes"], "growth": "High", "visa": "Medium"},
    {"role": "Renewable Energy Analyst", "category": "Immediate fit", "match": 84, "salary": "$85k-$120k", "missing": ["PPA/commercial modelling"], "growth": "High", "visa": "Medium-high"},
    {"role": "Electricity Forecasting Analyst", "category": "Strong fit (6-12 months)", "match": 82, "salary": "$100k-$135k", "missing": ["Forecast operations", "Weather feature pipelines"], "growth": "High", "visa": "Medium-high"},
    {"role": "BESS Analyst", "category": "Strong fit (6-12 months)", "match": 80, "salary": "$105k-$145k", "missing": ["BESS revenue stack", "SOC/degradation modelling"], "growth": "Very high", "visa": "Medium"},
    {"role": "Energy Market Modeller", "category": "Strong fit (6-12 months)", "match": 78, "salary": "$110k-$150k", "missing": ["PLEXOS/Aurora depth", "Scenario modelling"], "growth": "Very high", "visa": "Medium"},
    {"role": "DER Analyst", "category": "Strong fit (6-12 months)", "match": 78, "salary": "$95k-$135k", "missing": ["DERMS", "VPP and metering workflows"], "growth": "Very high", "visa": "Medium-high"},
    {"role": "Asset Performance Analyst - Energy", "category": "Immediate fit", "match": 86, "salary": "$90k-$130k", "missing": ["Renewable asset KPIs", "SCADA-to-analytics examples"], "growth": "High", "visa": "High"},
    {"role": "Regulatory / Market Analyst", "category": "Strong fit (6-12 months)", "match": 77, "salary": "$95k-$135k", "missing": ["NER/NEL regulatory depth", "Consultation paper experience"], "growth": "High", "visa": "Medium-high"},
    {"role": "Energy Systems Analyst", "category": "Immediate fit", "match": 87, "salary": "$90k-$125k", "missing": ["Australian market systems examples"], "growth": "High", "visa": "High"},
    {"role": "Trading Analyst - Power", "category": "Stretch / aspirational", "match": 72, "salary": "$120k-$180k+", "missing": ["Trading desk experience", "Risk/PnL", "Bidding strategy"], "growth": "Very high", "visa": "Lower-medium"},
    {"role": "Commercial Analyst - Renewables/BESS", "category": "Strong fit (6-12 months)", "match": 76, "salary": "$100k-$140k", "missing": ["PPA revenue models", "Project finance basics"], "growth": "High", "visa": "Medium"},
]

COMPANY_TIERS = {
    "Tier 1 Dream Companies": [
        "AEMO", "Transgrid", "Ausgrid", "EnergyAustralia", "AGL", "Origin Energy",
        "Snowy Hydro", "Hydro Tasmania", "Akaysha Energy", "Neoen", "TagEnergy",
        "Fluence", "Aurora Energy Research", "EY-Parthenon/ROAM", "Baringa",
    ],
    "Tier 2 Strong Opportunities": [
        "Endeavour Energy", "Essential Energy", "Iberdrola Australia", "Squadron Energy",
        "Tilt Renewables", "Tesla Energy", "Wartsila", "Jacobs", "GHD", "Aurecon",
        "AFRY", "Rystad Energy", "RepuTex", "ACIL Allen", "Shell Energy", "ENGIE",
    ],
    "Tier 3 Easier Entry Companies": [
        "Alinta Energy", "Ampol Energy", "GridBeyond", "Enel X", "Pacific Blue",
        "Edify Energy", "ACCIONA Energia", "Australian Energy Council", "ARENA",
        "CEFC", "NSW EnergyCo", "DCCEEW", "Universities and energy research centres",
    ],
}


def _fallback_strategy(jobs: list[Job]) -> dict:
    top_job = max(jobs, key=lambda job: job.score, default=None)
    return {
        "source": "rules",
        "headline": "Prioritise Business Analyst in Energy, Market Systems Analyst, Energy Data Analyst, Market Operations Analyst, and BESS pathways.",
        "top_roles": TARGET_ROLES,
        "company_tiers": COMPANY_TIERS,
        "next_actions": [
            "Apply first to AEMO, Transgrid, Ausgrid, EnergyAustralia, AGL, Origin, Akaysha, Fluence and Aurora Energy Research roles.",
            "Use Business Analyst in Energy | NEM Data | Utilities Transformation | Market Systems as the resume title for BA-heavy roles.",
            "Build one project that connects NEM price forecasting with BESS arbitrage and Power BI reporting.",
            "For each job, lead with AEMO NEMWeb ETL, price/demand forecasting, and Power BI market dashboards.",
        ],
        "fastest_path_120k": "Move from Energy/Data Analyst into BESS analytics, market modelling, or trading analytics after 6-12 months of NEM/FCAS/PLEXOS evidence.",
        "best_learning_companies": ["AEMO", "Aurora Energy Research", "EY-Parthenon/ROAM", "Baringa", "Transgrid", "Akaysha Energy", "Fluence"],
        "current_best_job": f"{top_job.title} at {top_job.company}" if top_job else "Fetch or add jobs to calculate live best fit.",
    }


async def build_targeting_strategy(jobs: list[Job]) -> dict:
    fallback = _fallback_strategy(jobs)
    try:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "source": {"type": "string"},
                "headline": {"type": "string"},
                "top_roles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "role": {"type": "string"},
                            "category": {"type": "string"},
                            "match": {"type": "integer"},
                            "salary": {"type": "string"},
                            "missing": {"type": "array", "items": {"type": "string"}},
                            "growth": {"type": "string"},
                            "visa": {"type": "string"},
                        },
                        "required": ["role", "category", "match", "salary", "missing", "growth", "visa"],
                    },
                },
                "company_tiers": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "Tier 1 Dream Companies": {"type": "array", "items": {"type": "string"}},
                        "Tier 2 Strong Opportunities": {"type": "array", "items": {"type": "string"}},
                        "Tier 3 Easier Entry Companies": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "Tier 1 Dream Companies",
                        "Tier 2 Strong Opportunities",
                        "Tier 3 Easier Entry Companies",
                    ],
                },
                "next_actions": {"type": "array", "items": {"type": "string"}},
                "fastest_path_120k": {"type": "string"},
                "best_learning_companies": {"type": "array", "items": {"type": "string"}},
                "current_best_job": {"type": "string"},
            },
            "required": [
                "source",
                "headline",
                "top_roles",
                "company_tiers",
                "next_actions",
                "fastest_path_120k",
                "best_learning_companies",
                "current_best_job",
            ],
        }
        job_context = [
            {"title": job.title, "company": job.company, "location": job.location, "score": job.score}
            for job in sorted(jobs, key=lambda item: item.score, reverse=True)[:12]
        ]
        result = await OpenAIService().structured_json(
            system="Act as a senior Australian energy industry career strategist, recruiter, and hiring manager. Return structured JSON only.",
            user=f"{PROFILE_SUMMARY}\nLive jobs context: {job_context}\nCreate a concise dashboard strategy for 2026-2028.",
            schema_name="career_targeting_strategy",
            schema=schema,
        )
        result["source"] = "openai"
        return result
    except Exception:
        return fallback
