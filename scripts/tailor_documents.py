"""
Uses the Anthropic API to tailor your master profile toward a specific job
description, then renders the result as ATS-friendly .docx files.

Requires your own Anthropic API key (console.anthropic.com) set as the
ANTHROPIC_API_KEY environment variable / GitHub secret. This is a paid API —
cost is a few cents per job with the model below.
"""

import json
import os
import re

import anthropic
from docx import Document
from docx.shared import Pt

# Cheapest current model — good enough for this task, run at scale daily.
# Swap to "claude-sonnet-5" in the model= call below if you want higher
# quality tailoring and don't mind the extra cost.
MODEL = "claude-haiku-4-5-20251001"

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def build_prompt(profile: dict, job: dict) -> str:
    return f"""You are tailoring a job application. Use ONLY facts from the
candidate profile below — never invent employers, dates, tools, or
achievements. Reword and reorder existing bullets to mirror the language of
the job description; do not fabricate new experience.

CANDIDATE PROFILE:
{json.dumps(profile, indent=2)}

JOB TITLE: {job['title']}
COMPANY: {job['company']}
JOB DESCRIPTION:
{job['description']}

Return ONLY valid JSON (no markdown fences, no preamble) with this exact
shape:
{{
  "tailored_summary": "2-3 sentence professional summary tailored to this role",
  "experience": [
    {{"title": "...", "company": "...", "dates": "...", "bullets": ["...", "..."]}}
  ],
  "cover_letter": "Full cover letter text, 3-4 paragraphs, addressed generically
    ('Dear Hiring Manager') unless a name is given in the job description."
}}

Keep resume bullets truthful, specific, and ATS-friendly (no special
characters, plain language, keywords from the job description worked in
naturally where they are genuinely supported by the candidate's real
experience)."""


def call_claude(profile: dict, job: dict) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": build_prompt(profile, job)}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)


def safe_filename(*parts: str) -> str:
    name = "_".join(parts)
    return re.sub(r"[^A-Za-z0-9_-]", "", name.replace(" ", "_"))[:80]


def write_resume_docx(profile: dict, tailored: dict, path: str) -> None:
    doc = Document()

    name = doc.add_heading(profile["personal"]["name"], level=1)
    name.runs[0].font.size = Pt(18)

    contact = doc.add_paragraph(
        f"{profile['personal']['location']} | {profile['personal']['phone']} | "
        f"{profile['personal']['email']} | {profile['personal']['linkedin']}"
    )
    contact.runs[0].font.size = Pt(10)

    doc.add_heading("Professional summary", level=2)
    doc.add_paragraph(tailored["tailored_summary"])

    doc.add_heading("Core skills", level=2)
    doc.add_paragraph(" | ".join(profile["core_skills"]))

    doc.add_heading("Professional experience", level=2)
    for role in tailored["experience"]:
        p = doc.add_paragraph()
        p.add_run(f"{role['title']} - {role['company']}").bold = True
        p.add_run(f"  ({role['dates']})")
        for bullet in role["bullets"]:
            doc.add_paragraph(bullet, style="List Bullet")

    doc.add_heading("Education", level=2)
    for edu in profile["education"]:
        doc.add_paragraph(f"{edu['degree']} - {edu['institution']} ({edu['date']})")

    doc.add_heading("Certifications", level=2)
    for cert in profile["certifications"]:
        doc.add_paragraph(cert, style="List Bullet")

    doc.save(path)


def write_cover_letter_docx(profile: dict, tailored: dict, path: str) -> None:
    doc = Document()
    doc.add_paragraph(profile["personal"]["name"])
    doc.add_paragraph(profile["personal"]["email"])
    doc.add_paragraph("")
    for paragraph in tailored["cover_letter"].split("\n\n"):
        doc.add_paragraph(paragraph.strip())
    doc.save(path)


def tailor_and_render(profile: dict, job: dict, output_dir: str) -> dict:
    tailored = call_claude(profile, job)

    base = safe_filename(job["company"], job["title"])
    resume_path = os.path.join(output_dir, f"{base}_resume.docx")
    cover_path = os.path.join(output_dir, f"{base}_cover_letter.docx")

    write_resume_docx(profile, tailored, resume_path)
    write_cover_letter_docx(profile, tailored, cover_path)

    return {
        "resume_file": os.path.basename(resume_path),
        "cover_letter_file": os.path.basename(cover_path),
    }
