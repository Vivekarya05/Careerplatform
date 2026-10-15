import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import httpx

from app.core.config import settings
from app.models.job import JobCreate, JobSource


SUPPORTED_SOURCES = [
    JobSource.seek,
    JobSource.indeed,
    JobSource.gradconnection,
    JobSource.prosple,
    JobSource.ethicaljobs,
    JobSource.company,
    JobSource.gmail,
    JobSource.manual_linkedin,
    JobSource.adzuna,
]

ENERGY_QUERIES = [
    "business analyst energy markets Australia",
    "business analyst utilities Australia",
    "business analyst trading systems energy Australia",
    "business analyst market systems electricity Australia",
    "business analyst renewable energy Australia",
    "business analyst BESS Australia",
    "utilities transformation business analyst Australia",
    "energy software business analyst Australia",
    "metering business analyst Australia",
    "DER analyst Australia",
    "asset performance analyst energy Australia",
    "commercial analyst energy Australia",
    "portfolio analyst energy Australia",
    "regulatory market analyst energy Australia",
    "market systems analyst Australia",
    "energy market analyst",
    "energy market modeller",
    "BESS analyst",
    "battery energy storage analyst",
    "electricity forecasting analyst",
    "trading analyst energy",
    "renewable energy analyst",
    "AEMO analyst",
    "Power BI energy analyst",
    "energy data analyst Australia",
    "market operations analyst electricity",
    "renewable energy trading analyst",
    "NEM analyst battery",
    "energy analyst Sydney",
    "energy analyst Melbourne",
    "battery storage analyst Australia",
    "electricity market analyst Australia",
    "renewable energy analyst Australia",
    "power systems analyst Australia",
    "utilities data analyst Australia",
    "energy systems analyst Australia",
]

ENERGY_KEYWORDS = (
    "aemo",
    "nem",
    "energy",
    "electricity",
    "power",
    "renewable",
    "battery",
    "bess",
    "dispatch",
    "fcas",
    "forecast",
    "trading",
    "market analyst",
    "market operations",
    "commercial analyst",
    "data analyst",
    "portfolio analyst",
    "grid",
    "transmission",
    "generator",
    "generation",
    "revenue",
    "revenue analytics",
    "power bi",
    "sql",
    "python",
    "utility",
    "utilities",
    "retailer",
    "network",
    "networks",
    "generator",
    "generators",
    "renewable developer",
    "energy software",
    "metering",
    "market systems",
    "trading systems",
    "distributed energy",
    "asset management",
    "asset performance",
    "regulatory",
    "utilities transformation",
)

TARGET_ROLE_KEYWORDS = (
    "analyst",
    "business analyst",
    "modeller",
    "modeler",
    "forecast",
    "market",
    "trading",
    "dispatch",
    "portfolio",
    "commercial",
    "data",
    "power bi",
    "business intelligence",
    "operations",
    "bess",
    "battery",
    "renewable",
    "grid",
    "network",
    "planning",
    "consultant",
    "graduate",
    "systems analyst",
    "market systems",
    "trading systems",
    "asset performance",
    "regulatory",
    "der",
    "distributed energy",
    "metering",
    "transformation",
)

EXCLUDED_ROLE_KEYWORDS = (
    "finance",
    "finanzen",
    "accountant",
    "accounts payable",
    "payroll",
    "tax",
    "treasury",
    "controller",
    "bookkeeper",
    "leiter finanzen",
    "head of finance",
    "chief financial",
    "sales manager",
    "marketing",
    "human resources",
    "hr ",
    "people partner",
    "legal counsel",
    "procurement manager",
    "warehouse",
    "mechanic",
    "nurse",
    "chef",
)

AUSTRALIA_LOCATION_KEYWORDS = (
    "australia",
    "sydney",
    "melbourne",
    "brisbane",
    "perth",
    "adelaide",
    "canberra",
    "hobart",
    "darwin",
    "gold coast",
    "newcastle",
    "wollongong",
    "nsw",
    "vic",
    "qld",
    "wa",
    "sa",
    "act",
    "tas",
    "nt",
)

INDIA_LOCATION_KEYWORDS = (
    "india",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "chennai",
    "mumbai",
    "pune",
    "delhi",
    "gurugram",
    "gurgaon",
    "noida",
    "ahmedabad",
    "kolkata",
    "andhra",
    "telangana",
    "karnataka",
    "tamil nadu",
    "maharashtra",
)

COUNTRY_KEYWORDS = {
    "australia": AUSTRALIA_LOCATION_KEYWORDS,
    "india": INDIA_LOCATION_KEYWORDS,
}

ADZUNA_COUNTRY_CODES = {
    "australia": "au",
}

HTML_TAG_RE = re.compile(r"<[^>]+>")
ANCHOR_RE = re.compile(r'<a[^>]+href=["\'](?P<href>[^"\']+)["\'][^>]*>(?P<label>.*?)</a>', re.IGNORECASE | re.DOTALL)


def _all_targets_requested(countries: list[str] | None = None) -> bool:
    return any(country.strip().lower() in {"all", "all target companies", "all companies"} for country in (countries or []))


def _selected_countries(countries: list[str] | None = None) -> list[str]:
    if _all_targets_requested(countries):
        return []
    return countries or settings.discovery_country_list


def _text(value: Any) -> str:
    return HTML_TAG_RE.sub(" ", str(value or "")).strip()


def _date(value: Any):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _looks_relevant(job: JobCreate) -> bool:
    haystack = f"{job.title} {job.company} {job.description}".lower()
    return any(_contains_keyword(haystack, keyword) for keyword in ENERGY_KEYWORDS)


def _contains_keyword(text: str, keyword: str) -> bool:
    cleaned = keyword.lower()
    if len(cleaned) <= 3:
        return bool(re.search(rf"\b{re.escape(cleaned)}\b", text))
    return cleaned in text


def _is_target_role(job: JobCreate) -> bool:
    title = (job.title or "").lower()
    haystack = f"{job.title} {job.description}".lower()
    if any(keyword in title for keyword in EXCLUDED_ROLE_KEYWORDS):
        return False
    energy_context = any(_contains_keyword(haystack, keyword) for keyword in ENERGY_KEYWORDS)
    business_analyst_context = (
        "business analyst" in title
        and any(
            _contains_keyword(haystack, keyword)
            for keyword in [
                "energy",
                "electricity",
                "utilities",
                "utility",
                "market systems",
                "trading systems",
                "metering",
                "der",
                "renewable",
                "bess",
                "network",
                "asset management",
            ]
        )
    )
    if not any(_contains_keyword(haystack, keyword) for keyword in TARGET_ROLE_KEYWORDS):
        return False
    return energy_context or business_analyst_context


def _allowed_country_keywords(countries: list[str] | None = None) -> tuple[str, ...]:
    selected = _selected_countries(countries)
    keywords: list[str] = []
    for country in selected:
        keywords.extend(COUNTRY_KEYWORDS.get(country.strip().lower(), (country.strip().lower(),)))
    return tuple(keyword for keyword in keywords if keyword)


def _is_allowed_location(job: JobCreate, countries: list[str] | None = None) -> bool:
    if _all_targets_requested(countries):
        return True
    location = (job.location or "").lower()
    source = job.source.value if hasattr(job.source, "value") else str(job.source)
    keywords = _allowed_country_keywords(countries)
    if source == JobSource.adzuna.value:
        return any(keyword in location for keyword in keywords) if keywords else True
    return any(keyword in location for keyword in keywords)


def is_allowed_country(job: JobCreate, countries: list[str] | None = None) -> bool:
    return _is_allowed_location(job, countries)


def is_target_australian_energy_job(job: JobCreate, countries: list[str] | None = None) -> bool:
    return bool(job.title and job.company and _is_allowed_location(job, countries) and _is_target_role(job))


def _dedupe(jobs: list[JobCreate]) -> list[JobCreate]:
    seen: set[str] = set()
    deduped: list[JobCreate] = []
    for job in jobs:
        key = f"{job.title.lower()}|{job.company.lower()}|{str(job.url or '').lower()}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)
    return deduped


def _selected_adzuna_countries(countries: list[str] | None = None) -> list[tuple[str, str]]:
    if _all_targets_requested(countries):
        selected = ["Australia"]
    else:
        selected = countries or settings.discovery_country_list
    resolved: list[tuple[str, str]] = []
    for country in selected:
        key = country.strip().lower()
        code = ADZUNA_COUNTRY_CODES.get(key)
        if code:
            resolved.append((key.title(), code))
    return resolved or [("Australia", "au")]


async def _discover_adzuna(client: httpx.AsyncClient, countries: list[str] | None = None) -> list[JobCreate]:
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        return []

    jobs: list[JobCreate] = []
    for country_name, country_code in _selected_adzuna_countries(countries):
        where = country_name if country_code != "au" else settings.discovery_location
        for query in ENERGY_QUERIES:
            response = await client.get(
                f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1",
                params={
                    "app_id": settings.adzuna_app_id,
                    "app_key": settings.adzuna_app_key,
                    "results_per_page": max(1, min(settings.discovery_results_per_source, 20)),
                    "what": query,
                    "where": where,
                    "sort_by": "date",
                    "content-type": "application/json",
                },
            )
            if response.status_code >= 400:
                continue
            for item in response.json().get("results", []):
                location = item.get("location", {}).get("display_name") or country_name
                company = item.get("company", {}).get("display_name") or "Unknown company"
                jobs.append(
                    JobCreate(
                        title=_text(item.get("title")) or query.title(),
                        company=_text(company),
                        location=_text(location),
                        source=JobSource.adzuna,
                        url=item.get("redirect_url"),
                        description=_text(item.get("description")),
                        salary_min=item.get("salary_min"),
                        salary_max=item.get("salary_max"),
                        posted_at=_date(item.get("created")),
                    )
                )
    return jobs


def _absolute_url(base_url: str, href: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return urljoin(base_url, href)


async def _discover_company_pages(client: httpx.AsyncClient, countries: list[str] | None = None) -> list[JobCreate]:
    jobs: list[JobCreate] = []
    selected = {country.strip().lower() for country in _selected_countries(countries)}
    for company, url, country in settings.company_career_source_list:
        if selected and country.strip().lower() not in selected:
            continue
        response = await client.get(url)
        if response.status_code >= 400:
            continue
        html = response.text
        for match in ANCHOR_RE.finditer(html):
            label = _text(match.group("label"))
            href = match.group("href")
            text = f"{label} {href} {company}"
            if not label or not _looks_relevant(JobCreate(title=label, company=company, description=text)):
                continue
            jobs.append(
                JobCreate(
                    title=label[:140],
                    company=company,
                    location=country,
                    source=JobSource.company,
                    url=_absolute_url(url, href),
                    description=f"{label} from {company} careers page. Review the source page for the full description.",
                )
            )
    return jobs


async def _discover_career_nest(client: httpx.AsyncClient) -> list[JobCreate]:
    jobs: list[JobCreate] = []
    for page in range(1, 9):
        response = await client.get(
            "https://careernest.cloud/api/feed",
            params={
                "page": page,
                "limit": 50,
            },
        )
        if response.status_code >= 400:
            continue
        for item in response.json().get("jobs", []):
            salary = item.get("salary") or {}
            jobs.append(
                JobCreate(
                    title=_text(item.get("title")),
                    company=_text(item.get("company")) or "Unknown company",
                    location=_text(item.get("location")) or "Australia",
                    source=JobSource.career_nest,
                    url=item.get("apply_url") or item.get("job_url"),
                    description=_text(item.get("description")),
                    salary_min=salary.get("min"),
                    salary_max=salary.get("max"),
                    posted_at=_date(item.get("posted_at")),
                )
            )
    return jobs


async def _discover_arbeitnow(client: httpx.AsyncClient) -> list[JobCreate]:
    jobs: list[JobCreate] = []
    for page in range(1, 6):
        response = await client.get(
            "https://www.arbeitnow.com/api/job-board-api",
            params={"page": page},
        )
        if response.status_code >= 400:
            continue
        for item in response.json().get("data", []):
            jobs.append(
                JobCreate(
                    title=_text(item.get("title")),
                    company=_text(item.get("company_name")) or "Unknown company",
                    location=_text(item.get("location")) or "Remote",
                    source=JobSource.arbeitnow,
                    url=item.get("url"),
                    description=_text(item.get("description")),
                    posted_at=_date(item.get("created_at")),
                )
            )
    return jobs


async def _ai_verify_jobs(jobs: list[JobCreate]) -> list[JobCreate]:
    if not settings.openai_api_key or not jobs:
        return jobs
    from app.services.openai_service import OpenAIService

    candidates = [
        {
            "index": index,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": (job.description or "")[:700],
        }
        for index, job in enumerate(jobs[:60])
    ]
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "index": {"type": "integer"},
                        "include": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": ["index", "include", "reason"],
                },
            }
        },
        "required": ["decisions"],
    }
    try:
        result = await OpenAIService().structured_json(
            system=(
                "You are an Australian energy-market hiring analyst. Keep only jobs that are in Australia "
                "and relevant to Business Analyst in Energy, Business Analyst - Utilities, Business Analyst - Energy Markets, "
                "Trading Systems Business Analyst, Market Systems Analyst, Operations Analyst - Energy, Commercial Analyst - Energy, "
                "Asset Performance Analyst, Energy Systems Analyst, Regulatory or Market Analyst, DER Analyst, Energy Market Analyst, "
                "Energy Market Modeller, BESS Analyst, Forecasting Analyst, Trading Analyst, Energy Data Analyst, Renewable Energy Analyst, "
                "Market Operations Analyst, Power BI Analyst in energy, or graduate energy analytics. Reject generic business analyst roles "
                "without energy/utilities context. Reject finance/accounting, HR, sales, "
                "generic management, and non-Australian roles. Return JSON only."
            ),
            user=f"Verify these job candidates for Vivek's Australian energy analytics job search: {candidates}",
            schema_name="job_discovery_verification",
            schema=schema,
        )
    except Exception:
        return jobs
    include_indexes = {
        decision["index"]
        for decision in result.get("decisions", [])
        if decision.get("include") is True and isinstance(decision.get("index"), int)
    }
    if not include_indexes:
        return jobs
    verified = [job for index, job in enumerate(jobs[:60]) if index in include_indexes]
    verified.extend(jobs[60:])
    return verified


async def discover_jobs(countries: list[str] | None = None) -> list[JobCreate]:
    """Discover live jobs from approved Australian-first sources.

    LinkedIn is intentionally excluded. Adzuna is used when free API credentials
    are configured. Company pages are used as a conservative fallback. Global
    no-key feeds are intentionally excluded because they produced non-Australian
    false positives.
    """
    timeout = httpx.Timeout(16.0, connect=8.0)
    headers = {"User-Agent": "Vivek Career Intelligence Platform/1.0"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        discovered: list[JobCreate] = []
        adapters = (
            lambda http_client: _discover_adzuna(http_client, countries),
            lambda http_client: _discover_company_pages(http_client, countries),
        )
        for adapter in adapters:
            try:
                discovered.extend(await adapter(client))
            except (httpx.HTTPError, ValueError, TypeError):
                continue

    relevant = [
        job
        for job in discovered
        if is_target_australian_energy_job(job, countries)
    ]
    verified = await _ai_verify_jobs(_dedupe(relevant))
    return verified[: max(10, settings.discovery_results_per_source * 4)]
