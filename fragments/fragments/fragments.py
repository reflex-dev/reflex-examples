"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from rxconfig import config

import reflex as rx

docs_url = "https://reflex.dev/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    """The app state."""

    pass


def raw_fragment_intro():
    """Raw fragment: Return a raw list of Reflex components, and use * to use the fragment."""
    return [
        rx.heading("This is a raw fragment", font_size="2em"),
        rx.box("Just regular Python! Use these with the * operator."),
    ]


def react_fragment_intro():
    """React fragment: Wrap the result into a `rx.fragment` to take advantage of React fragments. Use normally."""
    return rx.fragment(
        rx.heading("This is a React fragment", font_size="2em"),
        rx.box(
            "Read the fragment docs at ",
            rx.link("https://reactjs.org/docs/fragments.html"),
        ),
    )


def index():
    return rx.center(
        rx.vstack(
            *raw_fragment_intro(),
            react_fragment_intro(),
            rx.link(
                "Check out our docs!",
                href=docs_url,
                border="0.1em solid",
                padding="0.5em",
                border_radius="0.5em",
                _hover={
                    "color": "rgb(107,99,246)",
                },
            ),
            spacing="1.5em",
            font_size="2em",
        ),
        padding_top="10%",
    )


# Add state and page to the app.
app = rx.App(state=State)
app.add_page(index)
