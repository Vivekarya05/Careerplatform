import argparse
import asyncio

from app.agents.job_discovery import discover_jobs
from app.core.config import settings
from app.services.digest_service import build_digest
from app.services.email_service import EmailService
from app.services import job_store
from app.services.job_scoring import score_job


async def run_discovery() -> None:
    jobs = await discover_jobs()
    saved = 0
    skipped = 0
    for job in jobs:
        recommendation = score_job(job)
        created = await job_store.create_job_if_new(settings.career_user_id, job)
        if created:
            saved += 1
            print(f"{recommendation.job_score:3d} saved {job.title} - {job.company}")
        else:
            skipped += 1
            print(f"{recommendation.job_score:3d} existing {job.title} - {job.company}")
    print(f"Discovery complete: {saved} saved, {skipped} skipped, {len(jobs)} matched.")


async def send_digest(period: str) -> None:
    jobs = await job_store.list_jobs(settings.career_user_id)
    digest = build_digest(period, jobs)
    try:
        await EmailService().send_digest(digest)
    except RuntimeError as exc:
        print(f"Digest preview generated but not sent: {exc}")
        print(digest.subject)


def main() -> None:
    parser = argparse.ArgumentParser(description="Career Intelligence scheduler commands")
    parser.add_argument("command", choices=["discover", "digest"])
    parser.add_argument("--period", choices=["morning", "evening", "test"], default="morning")
    args = parser.parse_args()
    if args.command == "discover":
        asyncio.run(run_discovery())
    if args.command == "digest":
        asyncio.run(send_digest(args.period))


if __name__ == "__main__":
    main()
