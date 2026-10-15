from app.models.job import Job
from app.services.resume_service import resume_filename


def draft_resume_strategy(job: Job) -> dict:
    return {
        "title": f"Resume for {job.title} at {job.company}",
        "format": "premium_energy_market_analytics_latex",
        "template": "resume/vivek_energy_resume.tex",
        "pdf_filename": resume_filename(job),
        "header_target_line": f"Target: {job.title} at {job.company}",
        "project_order": [
            job.score_breakdown.get("best_project_to_highlight", "NEM Market Intelligence & BESS Trading Platform"),
            "Electricity Demand Forecasting (ARIMA/XGBoost/LSTM)",
            "PostgreSQL + Power BI energy analytics dashboard",
        ],
        "rules": [
            "Do not add unverified work experience.",
            "Keep claims project-backed.",
            "Always use the premium LaTeX format in resume/vivek_energy_resume.tex.",
            "Save LaTeX source and generated PDF as a version.",
            "Name the PDF with Vivek, company, and role.",
        ],
    }
