from __future__ import annotations

from uuid import UUID  # trunk-ignore(ruff/TCH003)

from pydantic import BaseModel

from hackathon_project_tracker.otel import tracer


class Delta(BaseModel):
    role: str | None = None
    content: str | None = None


class Choice(BaseModel):
    index: int | None = None
    finish_reason: str | None = None
    message: Delta | None = None
    delta: Delta | None = None


class Usage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class ChatResponse(BaseModel):
    id: UUID | None = None
    model: str | None = None
    object: str | None = None
    created: int | None = None
    choices: list[Choice] | None = None
    usage: Usage | None = None

    def get_content(
        self: ChatResponse,
    ) -> str | None:
        with tracer.start_as_current_span("get_content") as span:
            if self.choices is not None and (first_choice := self.choices[0]) and first_choice.message is not None:
                return first_choice.message.content

            span.add_event(
                name="no_content_found_in_chat_response",
                attributes={
                    "chat_response": self.model_dump_json(),
                },
            )
            return None
