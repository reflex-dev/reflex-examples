from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from github import Github
from github.GithubException import GithubException

from hackathon_project_tracker import helper_utils
from hackathon_project_tracker.helper_logging import Severity, log
from hackathon_project_tracker.otel import tracer

if TYPE_CHECKING:
    from github.PullRequest import PullRequest
    from github.Repository import Repository


def create_repo_path(
    tokens: dict[
            str,
            str | None,
        ],
) -> str:
    tokens = helper_utils.check_tokens(
        tokens=tokens,
    )
    github_owner: str | None = tokens.get(
        "GITHUB_OWNER",
        None,
    )
    github_repo: str | None = tokens.get(
        "GITHUB_REPO",
        None,
    )
    if github_owner is None:
        raise AttributeError

    if github_repo is None:
        raise AttributeError

    github_repo_path: str = f"{github_owner}/{github_repo}"
    match len(github_repo_path):

        case 0 | 1:
            raise AttributeError

        case _:
            return github_repo_path


def set_up_client_from_tokens(
    tokens: dict[
            str,
            str | None,
        ],
) -> Github:
    error_message: str | None = None
    tokens = helper_utils.check_tokens(
        tokens=tokens,
    )
    log(
        the_log="Setting up client",
        severity=Severity.DEBUG,
        file=__file__,
    )
    github_owner: str | None = tokens.get(
        "GITHUB_OWNER",
        None,
    )
    if github_owner is None:
        error_message = "GITHUB_OWNER is not set"
        raise AttributeError(error_message)

    github_repo: str | None = tokens.get(
        "GITHUB_REPO",
        None,
    )
    if github_repo is None:
        error_message = "GITHUB_REPO is not set"
        raise AttributeError(error_message)


    github_client_id: str | None = tokens.get(
        "GITHUB_CLIENT_ID",
        None,
    )
    if github_client_id is None:
        error_message = "GITHUB_CLIENT_ID is not set"
        raise AttributeError(error_message)

    github_client_secret: str | None = tokens.get(
        "GITHUB_CLIENT_SECRET",
        None,
    )
    if github_client_secret is None:
        error_message = "GITHUB_CLIENT_SECRET is not set"
        raise AttributeError(error_message)

    github_client: Github = Github()
    github_client.get_oauth_application(
        client_id=github_client_id,
        client_secret=github_client_secret,
    )
    return github_client





def fetch_repo(
    repo_path: str,
    client: Github,
) -> Repository | None:
    with tracer.start_as_current_span("fetch_repo") as span:
        span.add_event(
            name="fetch_repo-started",
            attributes={
                "repo_path": repo_path,
            },
        )
        repo: Repository | None = None
        try:
            repo = client.get_repo(repo_path)
            span.add_event(
                name="fetch_repo-completed",
                attributes={
                "repo_path": repo_path,
                "repo_full_name": repo.full_name,
            },
            )

        except GithubException as e:
            span.record_exception(e)
            span.add_event(
                name="fetch_repo-error",
                attributes={
                    "repo_path": repo_path,
                },
            )

        return repo


def fetch_pull_requests(
    repo: Repository,
) -> Generator[PullRequest, None, None]:
    span_name: str = "fetch_pull_requests"
    with tracer.start_as_current_span(span_name) as span:
        span.add_event(
            name=f"{span_name}-started",
        )
        yield from repo.get_pulls(
            state="all",
            sort="updated",
            direction="desc",
        )
        span.add_event(
            name=f"{span_name}-completed",
        )


def fetch_pull_request_for_repo(
    repo: Repository,
) -> Generator[PullRequest, None, None]:
    span_name: str = "fetch_pull_request_for_repo"
    with tracer.start_as_current_span(span_name) as span:
        span.add_event(
            name=f"{span_name}-started",
        )
        yield from fetch_pull_requests(
            repo=repo,
        )
        span.add_event(
            name=f"{span_name}-completed",
        )

