import httpx

from app.core.config import settings
from app.models.digest import DigestPreview


class EmailService:
    async def send_digest(self, digest: DigestPreview) -> None:
        if not settings.resend_api_key:
            raise RuntimeError("RESEND_API_KEY is not configured")
        if not settings.email_from or "@" not in settings.email_from:
            raise RuntimeError("EMAIL_FROM must be a verified sender address or Resend domain sender")
        if not settings.email_to or "@" not in settings.email_to:
            raise RuntimeError("EMAIL_TO must be the inbox that receives your digest")
        payload = {
            "from": settings.email_from,
            "to": [settings.email_to],
            "subject": digest.subject,
            "html": digest.html,
            "text": digest.text,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json=payload,
            )
            if response.status_code >= 400:
                try:
                    detail = response.json().get("message") or response.text
                except ValueError:
                    detail = response.text
                raise RuntimeError(f"Resend rejected the digest email: {detail}")
