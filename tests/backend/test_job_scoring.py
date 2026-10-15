from app.models.job import JobCreate
from app.services.job_scoring import score_job


def test_bess_nem_role_scores_high() -> None:
    job = JobCreate(
        title="BESS Trading Analyst",
        company="AEMO adjacent energy firm",
        description="Python SQL NEM dispatch pricing FCAS battery storage forecasting Power BI",
    )
    recommendation = score_job(job)
    assert recommendation.job_score >= 85
    assert recommendation.best_project_to_highlight == "NEM Market Intelligence & BESS Trading Platform"


def test_generic_role_scores_lower() -> None:
    job = JobCreate(
        title="Business Analyst",
        company="Generic Services",
        description="Stakeholder workshops and reporting",
    )
    recommendation = score_job(job)
    assert recommendation.job_score < 60


def test_energy_business_analyst_scores_high() -> None:
    job = JobCreate(
        title="Business Analyst - Energy Markets",
        company="EnergyAustralia",
        location="Melbourne VIC Australia",
        description="Utilities transformation role supporting market systems, trading systems, metering, stakeholder requirements, SQL and Power BI.",
    )

    recommendation = score_job(job)
    assert recommendation.job_score >= 80
    assert "Business analyst in energy fit" in " ".join(recommendation.reasons)
    assert "AEMO" in recommendation.missing_keywords


def test_salary_estimate_for_australian_bess_role() -> None:
    recommendation = score_job(
        JobCreate(
            title="BESS Trading Analyst",
            company="EnergyCo",
            location="Sydney NSW",
            description="NEM battery storage trading analytics, dispatch pricing and FCAS.",
        )
    )

    assert recommendation.salary_estimate == "Expected range: $110k-$155k AUD"
    assert recommendation.job_score >= 80


def test_salary_estimate_for_indian_energy_role() -> None:
    recommendation = score_job(
        JobCreate(
            title="Energy Data Analyst",
            company="Power Analytics",
            location="Hyderabad India",
            description="SQL Python energy market forecasting dashboards.",
        )
    )

    assert recommendation.salary_estimate == "Expected range: ₹12-28 LPA"
