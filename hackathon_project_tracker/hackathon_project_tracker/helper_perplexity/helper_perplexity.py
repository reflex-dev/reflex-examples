from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from pydantic.dataclasses import dataclass

from hackathon_project_tracker.otel import tracer

if TYPE_CHECKING:
    from httpx import Response

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
    ) -> Client | None:
        with tracer.start_as_current_span("set_up_client_from_tokens") as span:
            token: str | None = tokens.get("PERPLEXITY_API_KEY")
            if token is None:
                span.add_event(
                    name="missing_tokens-perplexity",
                    attributes={
                        "missing_token": "PERPLEXITY_API_KEY",
                    },
                )
                return None

        return cls(
            token=token,
        )

    async def call_perplexity_api(
        self: Client,
        chat_completion: ChatCompletion,
    ) -> ChatResponse:
        with tracer.start_as_current_span("call_perplexity_api") as span:
            api_key = self.token
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
                span.record_exception(e)
                error_message: str = "Perplexity API request timed out"
                span.add_event(
                    name="perplexity_api_request_timed_out",
                    attributes={
                        "exception": str(e),
                        "error_message": error_message,
                    },
                )
                raise TimeoutError(error_message) from e

            return ChatResponse.model_validate(response.json())
