"""Portfolio website built with Reflex."""

import reflex as rx

from rxconfig import config
from portfolio.components.navbar import navbar
from portfolio.components.hero import hero
from portfolio.components.projects import projects
from portfolio.components.skills import skills
from portfolio.components.contact import contact
from portfolio.components.footer import footer
from portfolio.styles.theme import theme


class State(rx.State):
    """The app state."""
    # Theme state
    color_mode: str = "light"

    # Contact form state
    name: str = ""
    email: str = ""
    message: str = ""

    @rx.var
    def form_fields_filled(self) -> bool:
        """Check if all form fields are filled."""
        return bool(self.name and self.email and self.message)

    @rx.event
    def handle_submit(self):
        """Handle the contact form submission."""
        # Reset form fields after submission
        self.name = ""
        self.email = ""
        self.message = ""


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
        width="100%",
    )


app = rx.App(
    style={"font_family": "Inter, sans-serif"},
    theme=theme,
)
app.add_page(index)
