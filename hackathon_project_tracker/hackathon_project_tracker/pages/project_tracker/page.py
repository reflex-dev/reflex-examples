from __future__ import annotations

import reflex as rx
from reflex_ag_grid import ag_grid

from hackathon_project_tracker.models.project import Project
from hackathon_project_tracker.pages.project_tracker.constants import (
    AG_GRID_ID,
    AG_GRID_THEME,
    DEFAULT_DISTANCE_THRESHOLD_FOR_VECTOR_SEARCH,
    REPO_FILTER_INPUT_ID,
    REPO_SEARCH_INPUT_ID,
    REPO_SIMILARITY_THRESHOLD_MAX,
    REPO_SIMILARITY_THRESHOLD_MIN,
    REPO_SIMILARITY_THRESHOLD_STEP,
)
from hackathon_project_tracker.pages.project_tracker.state import State

AG_GRID_COLUMN_DEFINITIONS = Project.get_ag_grid_column_definitions()


def index() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.logo(),
            rx.color_mode.button(),
            margin_y="1em",
            width="100%",
            justify_content="space-between",
        ),
        rx.flex(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.button(
                            "Vector search with filter",
                            on_click=State.vector_search_filter,
                            margin_bottom="1em",
                        ),
                        rx.heading(State.distance_threshold),
                    ),
                    rx.slider(
                        id="distance-threshold-slider",
                        min=REPO_SIMILARITY_THRESHOLD_MIN,
                        max=REPO_SIMILARITY_THRESHOLD_MAX,
                        step=REPO_SIMILARITY_THRESHOLD_STEP,
                        default_value=DEFAULT_DISTANCE_THRESHOLD_FOR_VECTOR_SEARCH,
                        on_change=State.distance_threshold_setter,
                        on_value_commit=State.distance_threshold_commit,
                        width="100%",
                    ),
                ),
            ),
            rx.spacer(),
            rx.input(
                id=REPO_SEARCH_INPUT_ID,
                value=State.repo_path_search,
                placeholder="GitHub repo path e.g. reflex-dev/reflex",
                on_change=State.setter_repo_path_search,
                width="40%",
            ),
            rx.button(
                "Fetch repo data",
                on_click=State.fetch_repo_and_submit,
                margin_bottom="1em",
            ),
            justify_content="space-between",
            width="100%",
        ),
        rx.hstack(
            rx.vstack(
                rx.text_area(
                    id=REPO_FILTER_INPUT_ID,
                    value=State.current_filter_vector_search_text,
                    placeholder="Search keywords in repo description",
                    on_change=State.setter_repo_filter_vector_search_text,
                    width="100%",
                    min_width="380px",
                    height="100%",
                    min_height="100px",
                    resize="horizontal",
                ),
            ),
            rx.spacer(),
            rx.fragment(State.repo_card_stats),
            rx.fragment(State.repo_card_description),
            width="100%",
        ),
        ag_grid(
            id=AG_GRID_ID,
            column_defs=AG_GRID_COLUMN_DEFINITIONS,
            row_data=State.display_data,
            pagination=True,
            pagination_page_size=100,
            pagination_page_size_selector=[
                50,
                100,
            ],
            on_selection_changed=State.setter_repo_path_ag_grid_selection,
            theme=AG_GRID_THEME,
            width="100%",
            height="60vh",
        ),
        width="80%",
        margin="0 auto",
        spacing="4",
    )
