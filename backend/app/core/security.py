import httpx
import jwt
from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_authenticated_user(authorization: str | None = Header(default=None)) -> str:
    """Require a bearer token in production.

    Supabase RLS remains the primary database guard. For local MVP work, an unset
    Supabase JWT secret allows requests through with a development user id.
    """
    if settings.app_env == "development" and not settings.supabase_jwt_secret:
        return settings.demo_user_id
    if settings.public_access_enabled and not authorization:
        return settings.career_user_id
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()

    if settings.supabase_url and settings.supabase_service_role_key:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_service_role_key,
                },
            )
        if response.status_code == 200:
            user_id = response.json().get("id")
            if user_id:
                return user_id
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")

    try:
        claims = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token") from exc
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    return user_id
