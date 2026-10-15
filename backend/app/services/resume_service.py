import re
import shutil
import subprocess
from pathlib import Path

from app.core.config import settings
from app.models.job import Job

def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "resume" / "vivek_energy_resume.tex").exists():
            return parent
    raise RuntimeError("Resume template not found")


REPO_ROOT = _repo_root()
TEMPLATE_PATH = REPO_ROOT / "resume" / "vivek_energy_resume.tex"
OUTPUT_DIR = REPO_ROOT / "resume" / "generated"


def _latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return re.sub(r"_+", "_", cleaned)[:72] or "Role"


def resume_filename(job: Job) -> str:
    company = _slug(job.company)
    role = _slug(job.title)
    return f"Vivek_Aryasomayajula_{company}_{role}_Resume.pdf"


def render_latex(job: Job) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return (
        template.replace("{{JOB_TITLE}}", _latex_escape(job.title))
        .replace("{{COMPANY}}", _latex_escape(job.company))
    )


def build_resume_artifact(job: Job) -> dict:
    pdf_filename = resume_filename(job)
    tex_filename = pdf_filename.replace(".pdf", ".tex")
    job_dir = OUTPUT_DIR / _slug(job.company)
    job_dir.mkdir(parents=True, exist_ok=True)

    latex_source = render_latex(job)
    tex_path = job_dir / tex_filename
    tex_path.write_text(latex_source, encoding="utf-8")

    pdf_path = job_dir / pdf_filename
    pdf_generated = False
    compile_error = None

    if shutil.which("latexmk"):
        command = [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-outdir={job_dir}",
            str(tex_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        pdf_generated = result.returncode == 0 and pdf_path.exists()
        if not pdf_generated:
            compile_error = result.stderr or result.stdout[-2000:]
    else:
        compile_error = "latexmk is not installed in this environment"

    return {
        "title": f"Resume for {job.title} at {job.company}",
        "latex_source": latex_source,
        "tex_path": str(tex_path),
        "pdf_path": str(pdf_path) if pdf_generated else None,
        "pdf_filename": pdf_filename,
        "pdf_generated": pdf_generated,
        "compile_error": compile_error,
    }


def compiler_status() -> dict:
    latexmk_path = shutil.which("latexmk")
    return {
        "pdf_compiler": "latexmk",
        "available": bool(latexmk_path),
        "path": latexmk_path,
        "template": str(TEMPLATE_PATH),
        "output_directory": str(OUTPUT_DIR),
        "storage_bucket": settings.resume_storage_bucket,
        "message": (
            "PDF compiler is available. Resume button will generate PDF files."
            if latexmk_path
            else "PDF compiler unavailable. Resume button will return LaTeX until latexmk is installed in the backend image."
        ),
    }


def save_resume_version(user_id: str, job: Job, artifact: dict) -> dict:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return artifact
    from app.core.supabase_client import get_supabase

    try:
        storage_path = None
        if artifact["pdf_generated"] and artifact["pdf_path"]:
            pdf_path = Path(artifact["pdf_path"])
            storage_path = f"{user_id}/{job.id}/{artifact['pdf_filename']}"
            get_supabase().storage.from_(settings.resume_storage_bucket).upload(
                storage_path,
                pdf_path.read_bytes(),
                {"content-type": "application/pdf", "upsert": "true"},
            )

        response = (
            get_supabase()
            .table("resume_versions")
            .insert(
                {
                    "user_id": user_id,
                    "job_id": job.id,
                    "title": artifact["title"],
                    "latex_source": artifact["latex_source"],
                    "pdf_storage_path": storage_path,
                    "strategy": {
                        "template": "premium_energy_market_analytics",
                        "pdf_filename": artifact["pdf_filename"],
                        "pdf_generated": artifact["pdf_generated"],
                    },
                }
            )
            .execute()
        )
        artifact["resume_version_id"] = response.data[0]["id"] if response.data else None
        artifact["pdf_storage_path"] = storage_path
    except Exception as exc:
        if not settings.public_access_enabled:
            raise
        artifact["storage_warning"] = f"Saved locally on backend; Supabase resume storage unavailable: {exc}"
    return artifact
