from app.agents.job_discovery import _dedupe, _is_allowed_location, _looks_relevant, is_target_australian_energy_job
from app.models.job import JobCreate, JobSource


def test_relevance_filter_keeps_energy_roles() -> None:
    job = JobCreate(
        title="Energy Market Analyst",
        company="AEMO",
        source=JobSource.adzuna,
        description="NEM dispatch pricing FCAS forecasting SQL Python",
    )

    assert _looks_relevant(job)


def test_discovery_dedupes_title_company_url() -> None:
    jobs = [
        JobCreate(title="BESS Analyst", company="TagEnergy", url="https://example.com/job", description="BESS NEM"),
        JobCreate(title="BESS Analyst", company="TagEnergy", url="https://example.com/job", description="BESS NEM"),
    ]

    assert len(_dedupe(jobs)) == 1


def test_location_filter_keeps_australian_roles() -> None:
    job = JobCreate(
        title="Energy Market Analyst",
        company="AEMO",
        location="Sydney NSW",
        source=JobSource.company,
        description="NEM forecasting",
    )

    assert _is_allowed_location(job, ["Australia"])


def test_location_filter_keeps_indian_roles() -> None:
    job = JobCreate(
        title="Energy Analyst",
        company="Energy Firm",
        location="Hyderabad India",
        source=JobSource.company,
        description="Power market forecasting",
    )

    assert _is_allowed_location(job, ["India"])


def test_location_filter_rejects_non_australian_fallback_roles() -> None:
    job = JobCreate(
        title="Energy Analyst",
        company="Example",
        location="Berlin",
        source=JobSource.career_nest,
        description="Energy forecasting",
    )

    assert not _is_allowed_location(job, ["Australia", "India"])


def test_default_discovery_filter_is_australia_only() -> None:
    job = JobCreate(
        title="Energy Analyst",
        company="Example",
        location="Singapore",
        source=JobSource.company,
        description="Energy forecasting",
    )

    assert not _is_allowed_location(job, ["Australia"])


def test_target_filter_rejects_german_finance_roles() -> None:
    job = JobCreate(
        title="Head of Finance / Leiter Finanzen (m/w/d)",
        company="Forte Germany GmbH",
        location="Schwalbach am Taunus",
        source=JobSource.arbeitnow,
        description="Finance transformation in an energy company.",
    )

    assert not is_target_australian_energy_job(job, ["Australia"])


def test_target_filter_keeps_australian_bess_analyst_roles() -> None:
    job = JobCreate(
        title="BESS Trading Analyst",
        company="Akaysha Energy",
        location="Sydney NSW",
        source=JobSource.adzuna,
        description="NEM battery storage trading analytics, FCAS, dispatch pricing and forecasting.",
    )

    assert is_target_australian_energy_job(job, ["Australia"])


def test_target_filter_keeps_energy_business_analyst_roles() -> None:
    job = JobCreate(
        title="Business Analyst - Trading Systems",
        company="Origin Energy",
        location="Sydney NSW",
        source=JobSource.adzuna,
        description="Energy retail trading systems, market systems, metering, requirements, SQL and stakeholder delivery.",
    )

    assert is_target_australian_energy_job(job, ["Australia"])


def test_target_filter_rejects_generic_business_analyst_without_energy_context() -> None:
    job = JobCreate(
        title="Business Analyst",
        company="Generic SaaS",
        location="Sydney NSW",
        source=JobSource.adzuna,
        description="CRM requirements, payroll workflow, sales operations and stakeholder reporting.",
    )

    assert not is_target_australian_energy_job(job, ["Australia"])
