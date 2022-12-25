"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
from pcconfig import config

import pynecone as pc

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(pc.State):
    """The app state."""

    pass


def raw_fragment_intro():
    """Raw fragment: Return a raw list of Pynecone components, and use * to use the fragment."""
    return [
        pc.heading("This is a raw fragment", font_size="2em"),
        pc.box("Just regular Python! Use these with the * operator."),
    ]


def react_fragment_intro():
    """React fragment: Wrap the result into a `pc.fragment` to take advantage of React fragments. Use normally."""
    return pc.fragment(
        pc.heading("This is a React fragment", font_size="2em"),
        pc.box(
            "Read the fragment docs at ",
            pc.link("https://reactjs.org/docs/fragments.html"),
        ),
    )


def index():
    return pc.center(
        pc.vstack(
            *raw_fragment_intro(),
            react_fragment_intro(),
            pc.link(
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
app = pc.App(state=State)
app.add_page(index)
app.compile()
