from __future__ import annotations

import reflex as rx

from .constants import REPO_CARD_MAX_WIDTH, REPO_CARD_MIN_WIDTH, REPO_CARD_SIZE


def repo_card_skeleton(
    size: str = REPO_CARD_SIZE,
    min_width: str = REPO_CARD_MIN_WIDTH,
    max_width: str = REPO_CARD_MAX_WIDTH,
) -> rx.Component:
    return rx.skeleton(
        rx.card(
            "Skeleton card",
            size=size,
            min_width=min_width,
            max_width=max_width,
        ),
    )


def repo_card_description_component(
    description: str,
    size: str = REPO_CARD_SIZE,
    min_width: str = REPO_CARD_MIN_WIDTH,
    max_width: str = REPO_CARD_MAX_WIDTH,
) -> rx.Component:
    return rx.card(
        description,
        size=size,
            min_width=min_width,
        max_width=max_width,
    )


def repo_card_stats_component(
    repo_path: str,
    repo_url: str,
    stars: str,
    language: str,
    website_url: str,
    min_width: str = REPO_CARD_MIN_WIDTH,
    max_width: str = REPO_CARD_MAX_WIDTH,
    size: str = REPO_CARD_SIZE,
) -> rx.Component:
    return rx.card(
        rx.data_list.root(
            rx.data_list.item(
                rx.data_list.label("Repo"),
                rx.data_list.value(
                    rx.link(
                        repo_path,
                        href=repo_url,
                    ),
                ),
            ),
            rx.data_list.item(
                rx.data_list.label("Stars"),
                rx.data_list.value(stars),
            ),
            rx.data_list.item(
                rx.data_list.label("Language"),
                rx.data_list.value(language),
            ),
            rx.data_list.item(
                rx.data_list.label("Website"),
                rx.data_list.value(
                    rx.link(
                        website_url,
                        href=website_url,
                    ),
                ),
            ),
            size="1",
        ),
        size=size,
        min_width=min_width,
        max_width=max_width,
    )
