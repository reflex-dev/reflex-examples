"""Common components used by all demo pages."""

import dataclasses
import inspect
from functools import wraps
from pathlib import Path
from typing import Callable

import reflex as rx


@dataclasses.dataclass(frozen=True)
class AppPage:
    """A demo page."""

    route: str
    title: str
    description: str


_APP_PAGES: dict[str, AppPage] = {}


class DemoState(rx.State):
    """State for the demo pages."""

    @rx.var(cache=True)
    def pages(self) -> list[AppPage]:
        return [p for p in _APP_PAGES.values() if p.route != "/"]


def demo_dropdown() -> rx.Component:
    """Dropdown to navigate between demo pages."""

    return rx.select.root(
        rx.select.trigger(placeholder="Select Demo"),
        rx.select.content(
            rx.foreach(
                DemoState.pages,
                lambda page: rx.select.item(
                    rx.heading(page.title, size="3"), value=page.route
                ),
            )
        ),
        value=rx.cond(
            rx.State.router.page.path == "/",
            "",
            rx.State.router.page.path,
        ),
        on_change=rx.redirect,
    )


def page_template(page: Callable[[], rx.Component]) -> rx.Component:
    """Template for all pages."""
    page_data = _APP_PAGES[page.__name__]

    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.hstack(
            demo_dropdown(),
            rx.spacer(),
            rx.link(
                rx.heading("playground", size="4"),
                href="/",
            ),
            width="100%",
            align="center",
        ),
        rx.text(page_data.description, margin_left="10px", margin_top="5px"),
        page(),
        rx.logo(),
        size="4",
    )


@dataclasses.dataclass(frozen=True)
class ExtraTab:
    """Extra tab to add to the demo page."""

    trigger: rx.Component
    content: rx.Component


def badged_card(
    badge_content: rx.Component, card_content: rx.Component
) -> rx.Component:
    return rx.card(
        rx.inset(
            rx.badge(
                badge_content,
                width="100%",
                size="2",
                height="3em",
                radius="none",
            ),
            side="top",
            pb="current",
        ),
        card_content,
    )


def demo_tabs(page: Callable[[], rx.Component]) -> rx.Component:
    page_file = Path(inspect.getfile(page))
    page_source = page_file.read_text()
    relative_page_file = page_file.relative_to(
        Path(__file__).parent.parent.parent.parent.resolve()
    )
    readme_file = page_file.with_name("README.md")

    extra_tabs = []

    if readme_file.exists():
        readme = readme_file.read_text()
        relative_readme_file = relative_page_file.with_name("README.md")
        extra_tabs.append(
            ExtraTab(
                trigger=rx.tabs.trigger(
                    rx.hstack(rx.icon("book"), rx.text("Readme")), value="readme"
                ),
                content=rx.tabs.content(
                    badged_card(
                        badge_content=rx.code(str(relative_readme_file)),
                        card_content=rx.markdown(readme),
                    ),
                    value="readme",
                ),
            ),
        )

    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger(
                rx.hstack(rx.icon("eye"), rx.text("Example")), value="example"
            ),
            rx.tabs.trigger(
                rx.hstack(rx.icon("code"), rx.text("Source")), value="source"
            ),
            *[tab.trigger for tab in extra_tabs],
            margin_bottom="1em",
        ),
        rx.tabs.content(page(), value="example", height="fit-content"),
        rx.tabs.content(
            badged_card(
                badge_content=rx.code(str(relative_page_file)),
                card_content=rx.code_block(
                    page_source, language="python", show_line_numbers=True
                ),
            ),
            value="source",
        ),
        *[tab.content for tab in extra_tabs],
        default_value="example",
        margin_top="1em",
    )


def demo_template(page: Callable[[], rx.Component]) -> rx.Component:
    """Template for all demo pages."""

    @wraps(page)
    def _page_wrapper():
        return demo_tabs(page)

    return page_template(_page_wrapper)


def page(
    route: str, title: str, description: str, **kwargs
) -> Callable[[Callable], Callable]:
    """Decorator to add the demo page to the demo registry."""

    template = kwargs.pop("template", page_template)

    def decorator(page):
        _APP_PAGES[page.__name__] = AppPage(
            route=route, title=title, description=description
        )

        @rx.page(route=route, title=title, description=description, **kwargs)
        @wraps(page)
        def inner():
            return template(page)

        return inner

    return decorator


def demo(
    route: str, title: str, description: str, **kwargs
) -> Callable[[Callable], Callable]:
    return page(route, title, description, template=demo_template, **kwargs)
