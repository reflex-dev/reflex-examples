"""Models related to hackathon projects."""
# trunk-ignore-all(pyright/reportMissingTypeStubs)
from __future__ import annotations

import datetime  # trunk-ignore(ruff/TCH003)
from typing import TYPE_CHECKING, Any

from reflex_ag_grid import ag_grid
from sqlmodel import Field

from .base import Base

if TYPE_CHECKING:

    from github.Repository import Repository
    from reflex import Var
    from reflex_ag_grid.ag_grid import ColumnDef


class Project(Base, table=True): # trunk-ignore(pyright/reportGeneralTypeIssues,pyright/reportCallIssue)
    """A hackathon project."""

    stars: int
    repo_path: str
    language: str = Field(
        default="",
    )
    created_at: datetime.datetime
    website: str
    repo_url: str
    description: str = Field(
        default="",
    )

    def __hash__(
        self: Project,
    ) -> int:
        """The hash is based on the repository path, ensuring that each
        project can be uniquely identified by its repository path.

        Returns:
            int: The github repo path as an integer hash value.
        """
        return hash(self.repo_path)

    @classmethod
    def from_repo(
        cls: type[Project],
        repo: Repository,
    ) -> Project:
        return cls(
            stars=repo.stargazers_count,
            language=repo.language,
            created_at=repo.created_at,
            repo_path=repo.full_name,
            website=repo.homepage,
            repo_url=repo.html_url,
            description=repo.description,
        )

    @staticmethod
    def get_ag_grid_column_definitions() -> list[ColumnDef]:
        return [
            ag_grid.column_def(
                field="repo_path",
                header_name="Repo",
                filter=ag_grid.filters.text,
            ),
            ag_grid.column_def(
                field="stars",
                header_name="Stars",
                filter=ag_grid.filters.number,
            ),
            ag_grid.column_def(
                field="language",
                header_name="Language",
                filter=ag_grid.filters.text,
            ),
            ag_grid.column_def(
                field="created_at",
                header_name="Created at",
                filter=ag_grid.filters.date,
            ),
        ]

    @staticmethod
    def _format_for_data_list(
        item: tuple[str, str],
    ) -> tuple[str, str]:
        field, value = item
        match field:
            case "created_at":
                return "Created", value.strftime("%B %Y")

            case "stars":
                return "Stars", value

            case "repo_path":
                return "Repo", value

            case "language":
                return "Language", value

            case "website":
                return "Website", value

            case _:
                return field, value

    @staticmethod
    def format_value(
        field: str,
        value: object,
    ) -> object:
        match field:
            case _:
                return value

    def to_ag_grid_dict(
        self: Project,
    ) -> dict:
        def _formatted_key_values(
            field: str,
        ) -> tuple[str, Any]:
            return field, Project.format_value(
                field=field,
                value=getattr(
                    self,
                    field,
                ),
            )

        displayable_fields: list[str | Var[str]] = [
            column_def.field for column_def in Project.get_ag_grid_column_definitions()
        ]
        return dict(_formatted_key_values(field) for field in displayable_fields) ## trunk-ignore(pyright/reportArgumentType,pyright/reportCallIssue)

    def set_description(
        self: Project,
        description: str,
    ) -> None:
        self.description = description
