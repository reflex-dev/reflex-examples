"""Portfolio website built with Reflex."""

import reflex as rx

from rxconfig import config
from portfolio.components.navbar import navbar
from portfolio.components.hero import hero
from portfolio.components.projects import projects
from portfolio.components.skills import skills
from portfolio.components.contact import contact
from portfolio.components.footer import footer


class State(rx.State):
    """The app state."""
    pass


def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                hero(),
                projects(),
                skills(),
                contact(),
                max_width="1200px",
                width="100%",
                margin_x="auto",
                padding_x="4",
            )
        ),
        footer(),
        bg=rx.color_mode.current.bg,
        color=rx.color_mode.current.text,
    )


app = rx.App()
app.add_page(index)
