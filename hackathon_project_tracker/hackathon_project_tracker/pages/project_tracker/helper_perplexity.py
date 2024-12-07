from __future__ import annotations

from hackathon_project_tracker.helper_perplexity import (
    DEFAULT_PROMPT,
    ChatCompletion,
    ChatResponse,
    Client,
    Message,
)


async def perplexity_get_repo(
    repo_url: str,
    client: Client | None = None,
) -> str:
    if client is None:
        raise AssertionError("Client is required")

    content: str = DEFAULT_PROMPT.replace(
        "<link_to_github_repository>",
        repo_url,
    )
    chat_completion: ChatCompletion = ChatCompletion(
        messages=[
            Message(
                content=content,
            ),
        ],
    )
    chat_response: ChatResponse = await client.call_perplexity_api(
        chat_completion=chat_completion,
    )
    return chat_response.get_content()
