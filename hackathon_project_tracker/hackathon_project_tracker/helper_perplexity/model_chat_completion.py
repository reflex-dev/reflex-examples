from __future__ import annotations

from pydantic import BaseModel

DEFAULT_PROMPT: str = """
Give a short description of what this GitHub repository does <link_to_github_repository>.
Make sure to also include the primary programming language used.
"""


class Message(BaseModel):
    role: str = "user"
    content: str = DEFAULT_PROMPT


class ChatCompletion(BaseModel):
    model: str | None = "llama-3.1-sonar-small-128k-online"
    messages: list[Message] | None
    max_tokens: str | None = None
    temperature: float | None = 0.2
    top_p: float | None = 0.9
    return_citations: bool | None = True
    search_domain_filter: list[str] | None = ["perplexity.ai"]
    return_images: bool | None = False
    return_related_questions: bool | None = False
    search_recency_filter: str | None = "month"
    top_k: int | None = 0
    stream: bool | None = False
    presence_penalty: int | None = 0
    frequency_penalty: int | None = 1
