from __future__ import annotations

import httpx
from pydantic.dataclasses import dataclass
from requests import Response

from .model_chat_completion import ChatCompletion
from .model_chat_response import ChatResponse

BASE_API_URL: str = "https://api.perplexity.ai"
TIMEOUT: int = 30

@dataclass
class Client:
    token: str

    @classmethod
    def set_up_client_from_tokens(
        cls: type[Client],
        tokens: list[str],
    ) -> Client:
        token: str | None = tokens.get("PERPLEXITY_API_KEY")
        if token is None:
            raise ValueError("PERPLEXITY_API_KEY not found in tokens")

        return cls(
            token=token,
        )

    async def call_perplexity_api(
        self,
        chat_completion: ChatCompletion,
    ) -> ChatResponse:
        api_key = self.token
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")

        headers: dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=TIMEOUT,
            ) as client:
                response: Response = await client.post(
                    url=f"{BASE_API_URL}/chat/completions",
                    headers=headers,
                    data=chat_completion.model_dump_json(),
                )
                response.raise_for_status()

        except httpx.ReadTimeout as e:
            raise TimeoutError("Perplexity API request timed out") from e

        return ChatResponse.model_validate(response.json())
