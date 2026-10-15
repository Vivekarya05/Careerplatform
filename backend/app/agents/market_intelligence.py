from app.models.job import Job


def weekly_market_report(jobs: list[Job]) -> dict:
    companies = sorted({job.company for job in jobs})
    demanded_skills = ["BESS", "NEM", "forecasting", "Python", "SQL", "Power BI", "FCAS", "PLEXOS"]
    return {
        "title": "Australian Energy Hiring Intelligence",
        "jobs_reviewed": len(jobs),
        "repeated_hiring_firms": companies[:10],
        "demanded_skills": demanded_skills,
        "bess_growth_signal": "Track frequency of BESS, battery, storage, arbitrage, and grid-scale terms.",
        "salary_ranges": "Populate from job salary fields as discovered.",
        "recommendations": [
            "Prioritise AEMO, BESS owners, trading desks, and energy consultancies.",
            "Keep PLEXOS visible when the role mentions market modelling or consulting.",
        ],
    }

