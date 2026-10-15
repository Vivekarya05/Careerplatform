import base64
import re
from dataclasses import dataclass

import httpx

from app.core.config import settings


SKILL_KEYWORDS = (
    "AEMO",
    "NEM",
    "NEMWeb",
    "BESS",
    "Battery",
    "FCAS",
    "Dispatch Pricing",
    "Negative Pricing",
    "Forecasting",
    "Price Forecasting",
    "Demand Forecasting",
    "Time Series",
    "Python",
    "SQL",
    "PostgreSQL",
    "Power BI",
    "DAX",
    "Pandas",
    "NumPy",
    "XGBoost",
    "LSTM",
    "TensorFlow",
    "Keras",
    "Plotly",
    "Streamlit",
    "ETL",
    "Data Engineering",
    "Renewable Integration",
    "Market Intelligence",
    "PLEXOS",
)


@dataclass
class GithubProjectEvidence:
    repo: str
    url: str
    summary: str
    skills: list[str]


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "career-intelligence-platform",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    skills = [skill for skill in SKILL_KEYWORDS if skill.lower() in lowered]
    return sorted(dict.fromkeys(skills))


def _summarise_readme(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.replace("#", " ")).strip()
    if not cleaned:
        return "README detected but it does not include enough project detail yet."
    return cleaned[:420]


async def fetch_github_project_evidence(limit: int = 8) -> list[GithubProjectEvidence]:
    """Read public or token-accessible GitHub READMEs for interview evidence."""
    if not settings.github_username:
        return []

    async with httpx.AsyncClient(timeout=18, headers=_headers()) as client:
        response = await client.get(
            f"https://api.github.com/users/{settings.github_username}/repos",
            params={"sort": "updated", "per_page": min(max(limit, 1), 20)},
        )
        if response.status_code >= 400:
            return []

        projects: list[GithubProjectEvidence] = []
        for repo in response.json()[:limit]:
            name = repo.get("name")
            if not name:
                continue
            readme = await client.get(
                f"https://api.github.com/repos/{settings.github_username}/{name}/readme"
            )
            if readme.status_code >= 400:
                continue
            data = readme.json()
            encoded = data.get("content")
            if not encoded:
                continue
            try:
                text = base64.b64decode(encoded).decode("utf-8", errors="ignore")
            except ValueError:
                continue
            skills = _extract_skills(text)
            if not skills:
                continue
            projects.append(
                GithubProjectEvidence(
                    repo=name,
                    url=repo.get("html_url") or f"https://github.com/{settings.github_username}/{name}",
                    summary=_summarise_readme(text),
                    skills=skills,
                )
            )
    return projects


async def infer_github_skills() -> dict:
    projects = await fetch_github_project_evidence()
    skills: list[str] = []
    for project in projects:
        skills.extend(project.skills)
    return {
        "skills": sorted(dict.fromkeys(skills)),
        "projects": [project.__dict__ for project in projects],
        "source": "github_readmes" if projects else "fallback_profile",
    }
