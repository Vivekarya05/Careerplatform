import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings


class OpenAIService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def structured_json(self, system: str, user: str, schema_name: str, schema: dict[str, Any]) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        response = await self._client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        return json.loads(response.output_text)

