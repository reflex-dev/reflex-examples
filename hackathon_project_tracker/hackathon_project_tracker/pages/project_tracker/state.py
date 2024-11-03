from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import chromadb
import chromadb.api
import reflex as rx
from github import Github
from sqlalchemy import select
from sqlalchemy.orm import Session

from hackathon_project_tracker import helper_chroma, helper_perplexity
from hackathon_project_tracker.models.project import Project
from hackathon_project_tracker.otel import tracer
from hackathon_project_tracker.pages.project_tracker import helper_github
from hackathon_project_tracker.tokens import TOKENS

from .constants import (
    DEFAULT_DISTANCE_THRESHOLD_FOR_VECTOR_SEARCH,
    NUMBER_OF_RESULTS_TO_DISPLAY_FOR_VECTOR_SEARCH,
    NUMBER_OF_WORDS_TO_DISPLAY_FOR_REPO_DESCRIPTION,
)
from .helper_chroma import chroma_add_project, chroma_get_projects
from .helper_perplexity import perplexity_get_repo
from .repo_cards import (
    repo_card_description_component,
    repo_card_skeleton,
    repo_card_stats_component,
)

if TYPE_CHECKING:
    import chromadb.api.client
    from github.Repository import Repository
CHROMA_CLIENT: chromadb.HttpClient = helper_chroma.set_up_client_from_tokens(
    tokens=TOKENS,
)
GITHUB_CLIENT: Github = helper_github.set_up_client_from_tokens(
    tokens=TOKENS,
)
PERPLEXITY_CLIENT: helper_perplexity.Client = (
    helper_perplexity.Client.set_up_client_from_tokens(
        tokens=TOKENS,
    )
)


class State(rx.State):
    """The state for the project tracker page."""

    distance_threshold: int = DEFAULT_DISTANCE_THRESHOLD_FOR_VECTOR_SEARCH
    current_filter_vector_search_text: str = ""
    last_vector_search_filter_text: str = ""
    repo_path_search: str = ""
    ag_grid_selection_repo_path: str | None = None
    ag_grid_selection_project_index: int | None = None

    projects: list[Project] = []
    projects_to_commit: list[Project] = []
    display_data_indices: list[int] = []

    def distance_threshold_setter(
        self,
        value: list[int],
    ) -> None:
        self.distance_threshold = value[0]

    def distance_threshold_commit(
        self,
        value: list[int],
    ) -> None:
        del value
        self.vector_search_filter()

    @staticmethod
    def _find_project_index_using_repo_path(
        projects: list[Project],
        repo_path: str | None,
    ) -> Project | None:
        if repo_path is None:
            return None

        first_index = next(
            (i for i in range(len(projects)) if projects[i].repo_path == repo_path),
            None,
        )
        if first_index is None:
            return None

        return first_index

    @rx.var(cache=True)
    def has_selected_data(
        self,
    ) -> bool:
        return self.ag_grid_selection_repo_path is not None

    @rx.var(cache=True)
    def display_data(
        self,
    ) -> list[dict]:
        return [self.projects[i].to_ag_grid_dict() for i in self.display_data_indices]

    @rx.var
    def repo_card_stats(
        self,
    ) -> rx.Component:
        project_index: int | None = State._find_project_index_using_repo_path(
            projects=self.projects,
            repo_path=self.ag_grid_selection_repo_path,
        )
        if project_index is None:
            return rx.fragment(repo_card_skeleton())

        project: Project = self.projects[project_index]
        return rx.fragment(
            repo_card_stats_component(
                repo_path=project.repo_path,
                repo_url=f"https://github.com/{project.repo_path}",
                stars=f"{project.stars:,}",
                language=f"{project.language}",
                website_url=f"{project.website}",
            ),
        )

    @rx.var
    def repo_card_description(
        self,  # trunk-ignore(ruff/ANN10)
    ) -> rx.Component:
        project_index: int | None = State._find_project_index_using_repo_path(
            projects=self.projects,
            repo_path=self.ag_grid_selection_repo_path,
        )
        if project_index is None:
            return rx.fragment(
                repo_card_skeleton(),
            )

        project: Project = self.projects[project_index]
        description: str = str(project.description)
        if first_n_words_from_description := " ".join(
            project.description.split()[
                :NUMBER_OF_WORDS_TO_DISPLAY_FOR_REPO_DESCRIPTION
            ],
        ):
            description = first_n_words_from_description

        return rx.fragment(
            repo_card_description_component(
                description=description,
            ),
        )

    def setter_repo_path_search(
        self: State,
        repo_path: str,
    ) -> None:
        with tracer.start_as_current_span("setter_repo_path_search") as span:
            self.repo_path_search = repo_path
            span.add_event(
                name="repo_path_current-set",
                attributes={
                    "repo_path": str(self.repo_path_search),
                },
            )

    def clear_repo_path_search(
        self: State,
    ) -> None:
        with tracer.start_as_current_span("clear_repo_path_search") as span:
            self.repo_path_search = ""
            span.add_event(
                name="repo_path_current-clear",
            )

    def setter_repo_path_ag_grid_selection(
        self: State,
        rows: list[dict[str, str]],
        _0: int,
        _1: int,
    ) -> None:
        del _0, _1
        with tracer.start_as_current_span("setter_repo_path_ag_grid_selection") as span:
            if rows and (repo_path := rows[0].get("repo_path")):
                self.ag_grid_selection_repo_path = repo_path
                span.add_event(
                    name="selection_repo_path-set",
                    attributes={
                        "repo_path": str(self.ag_grid_selection_repo_path),
                    },
                )
                return

            span.add_event(
                name="selection_repo_path-unset",
            )

    def setter_repo_filter_vector_search_text(
        self: State,
        repo_filter_vector_search_text: str,
    ) -> None:
        with tracer.start_as_current_span(
            "setter_repo_filter_vector_search_text",
        ) as span:
            self.current_filter_vector_search_text = repo_filter_vector_search_text
            span.add_event(
                name="repo_filter_vector_search_text-set",
                attributes={
                    "repo_filter_vector_search_text": str(
                        self.current_filter_vector_search_text,
                    ),
                },
            )
            if not repo_filter_vector_search_text:
                return

            self.last_vector_search_filter_text = repo_filter_vector_search_text

    def display_data_indices_setter(
        self: State,
        display_data_indices: list[int],
    ) -> None:
        with tracer.start_as_current_span("display_data_indices_setter") as span:
            self.display_data_indices = display_data_indices
            span.add_event(
                name="display_data_indices-set",
                attributes={
                    "display_data_indices": str(self.display_data_indices),
                },
            )

    def add_project_to_display_data(
        self: State,
        project: Project,
    ) -> Generator[None, None, None]:
        with tracer.start_as_current_span("add_project_to_display_data") as span:

            def add_project() -> int:
                span.add_event(
                    name="project-add_project-started",
                    attributes={
                        "project_repo_path": str(project.repo_path),
                    },
                )
                self.projects.append(project)
                project_index = self._find_project_index_using_repo_path(
                    projects=self.projects,
                    repo_path=project.repo_path,
                )
                if project_index is None:
                    error_msg: str = (
                        f"Project should be non null and found in projects: {project.repo_path}"
                    )
                    raise AssertionError(error_msg)

                return project_index

            project_index: int | None = self._find_project_index_using_repo_path(
                projects=self.projects,
                repo_path=project.repo_path,
            )
            span.add_event(
                name="project-find_index-completed",
                attributes={
                    "project_repo_path": str(project.repo_path),
                    "project_index": str(project_index),
                },
            )
            if project_index is None:
                span.add_event(
                    name="project-add_project-queued",
                    attributes={
                        "project_repo_path": str(project.repo_path),
                    },
                )
                project_index = add_project()
                span.add_event(
                    name="project-add_project-completed",
                    attributes={
                        "project_repo_path": str(project.repo_path),
                    },
                )

            display_data_indices: list[int] = [*self.display_data_indices]
            span.add_event(
                name="display_data_indices-current",
                attributes={
                    "display_data_indices": str(display_data_indices),
                },
            )
            if project_index in display_data_indices:
                span.add_event(
                    name="project-already_in_display_data",
                    attributes={
                        "project_repo_path": str(project.repo_path),
                    },
                )

            if project_index not in display_data_indices:
                display_data_indices.append(project_index)
                self.display_data_indices_setter(
                    display_data_indices=display_data_indices,
                )
                span.add_event(
                    name="project-added_to_display_data",
                    attributes={
                        "project_repo_path": str(project.repo_path),
                    },
                )

    def _save_projects_to_db(
        self: State,
        projects: list[Project],
    ) -> Generator[None, None, None]:
        def filter_projects_to_save(
            db: Session,
            projects: list[Project],
        ) -> list[Project]:
            with tracer.start_as_current_span("get_new_projects") as span:
                span.add_event(
                    name="get_new_projects-started",
                    attributes={
                        "project_count-to_commit": len(projects),
                    },
                )
                existing_repo_paths: set[str] = {
                    str(path[0]) for path in db.query(Project.repo_path).all()
                }
                span.add_event(
                    name="get_new_projects-existing_repo_paths",
                    attributes={
                        "existing_repo_paths": str(existing_repo_paths),
                        "existing_repo_path_count": len(existing_repo_paths),
                        "existing_repo_path_type": str(type(existing_repo_paths)),
                    },
                )
                new_projects: list[Project] = [
                    project
                    for project in projects
                    if str(project.repo_path) not in existing_repo_paths
                ]
                span.add_event(
                    name="get_new_projects-completed",
                    attributes={
                        "project_count-to_save": len(new_projects),
                    },
                )
                return new_projects

        with tracer.start_as_current_span(
            "save_projects_to_db",
        ) as span, rx.session() as session:
            if not projects:
                span.add_event(
                    name="db-projects-no_projects_to_save",
                )
                return

            projects_to_save: list[Project] = filter_projects_to_save(
                db=session,
                projects=projects,
            )
            span.add_event(
                name="db-projects-projects_to_save",
                attributes={
                    "project_count": len(projects_to_save),
                },
            )
            if len(projects_to_save) == 0:
                span.add_event(
                    name="db-projects-no_new_projects_to_save",
                )
                if projects:
                    first_repo, *_ = projects
                    span.add_event(
                        name="db-projects-repo_already_saved",
                        attributes={
                            "repo_path": str(first_repo.repo_path),
                        },
                    )

                return

            session.bulk_save_objects(projects_to_save)
            session.commit()
            span.add_event(
                name="db-projects-added_to_db",
                attributes={
                    "project_count": len(projects_to_save),
                },
            )

    def save_project(
        self: State,
        project: Project,
    ) -> Generator[None, None, None]:
        with tracer.start_as_current_span("save_project") as span:
            self.projects_to_commit.append(project)
            span.add_event(
                name="projects_to_commit-added_project",
                attributes={
                    "project_repo_path": str(project.repo_path),
                },
            )
            yield from self._save_projects_to_db(
                projects=self.projects_to_commit,
            )

            span.add_event(
                name="projects_to_commit-saved_to_db",
            )
            self.projects_to_commit.clear()
            span.add_event(
                name="projects_to_commit-cleared",
            )

    @rx.background
    async def fetch_repo_and_submit(
        self: State,
    ):
        async with self:
            span = tracer.start_span("fetch_repo_and_submit")
            repo_path_search: str = helper_github.extract_repo_path_from_url(
                url=self.repo_path_search,
            )
            repo: Repository | None = helper_github.fetch_repo(
                repo_path=repo_path_search,
                client=GITHUB_CLIENT,
            )
            if repo is None:
                span_event_name: str = "repo-not_found"
                repo_path: str = self.repo_path_search
                self.clear_repo_path_search()
                yield rx.toast.error(
                    span_event_name,
                )

                span.add_event(
                    name=span_event_name,
                    attributes={
                        "repo_path": repo_path,
                    },
                )
                return

            span.add_event(
                name="repo-found",
                attributes={
                    "repo_path": str(repo.full_name),
                    "repo_description": str(repo.description),
                },
            )
            project: Project = Project.from_repo(
                repo=repo,
            )
            span.add_event(
                name="project-created_from_repo",
                attributes={
                    "project_repo_path": str(project.repo_path),
                    "project_stars": str(project.stars),
                    "project_language": str(project.language),
                    "project_website": str(project.website),
                    "project_description": str(project.description),
                    "project_created_at": str(project.created_at),
                },
            )
            self.add_project_to_display_data(project)
            self.clear_repo_path_search()
            yield

            perplexity_description: str = await perplexity_get_repo(
                repo_url=project.repo_url,
                client=PERPLEXITY_CLIENT,
            )
            project.set_description(
                description=perplexity_description,
            )
            yield

            for _ in self.save_project(project):
                yield

            yield

            chroma_add_project(
                project=project,
                client=CHROMA_CLIENT,
            )
            yield

    def vector_search_filter(
        self: State,
    ) -> Generator[rx.Component, None, None]:
        with tracer.start_as_current_span("vector_search_filter") as span:
            span.add_event(
                name="vector_search_filter-called",
                attributes={
                    "repo_filter_text": str(self.last_vector_search_filter_text),
                },
            )
            distance_threshold: float = self.distance_threshold / 100
            project_repo_paths: list[str] = chroma_get_projects(
                repo_filter_vector_search_text=self.last_vector_search_filter_text,
                n_results=NUMBER_OF_RESULTS_TO_DISPLAY_FOR_VECTOR_SEARCH,
                client=CHROMA_CLIENT,
                distance_threshold=distance_threshold,
            )
            if project_repo_paths is None or not project_repo_paths:
                return

            self.display_data_indices = [
                index
                for index in (
                    self._find_project_index_using_repo_path(
                        projects=self.projects,
                        repo_path=repo_path,
                    )
                    for repo_path in project_repo_paths
                )
                if index is not None
            ]

    def on_load(
        self: State,
    ) -> None:
        with tracer.start_as_current_span("on_load") as span:
            with rx.session() as session:
                self.projects = (
                    session.exec(
                        statement=select(Project),
                    )
                    .scalars()
                    .all()
                )

            span.add_event(
                name="projects-loaded",
                attributes={
                    "project_count": len(self.projects),
                },
            )
            self.display_data_indices = list(range(len(self.projects)))
