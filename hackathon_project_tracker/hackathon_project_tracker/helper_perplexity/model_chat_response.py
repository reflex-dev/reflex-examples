from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from hackathon_project_tracker.helper_logging import Severity, log


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
        if self.choices is not None and (first_choice := self.choices[0]):
            if first_choice.message is not None:
                return first_choice.message.content

        log(
            f"No content found in chat response: {self.model_dump_json()}",
            severity=Severity.ERROR,
            file=__file__,
        )
        return None
