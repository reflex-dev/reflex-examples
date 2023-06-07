"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
from pcconfig import config

import pynecone as pc

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"

COLOR_SCHEMES = [
    "blackAlpha",
    "gray",
    "red",
    "orange",
    "yellow",
    "green",
    "teal",
    "blue",
    "cyan",
    "purple",
    "pink",
    "linkedin",
    "facebook",
    "messenger",
    "whatsapp",
    "twitter",
    "telegram",
    "whiteAlpha",
]


class State(pc.State):
    """The app state."""

    color_scheme: str = COLOR_SCHEMES[0]


def theme_card(theme_name):
    """A theme card."""
    return pc.box(
        theme_name,
        border=1,
        border_radius="md",
        px=4,
        py=1,
    )


def theme_selector():
    """The theme selector."""
    return pc.box(
        pc.text("Color scheme", font_weight="semibold"),
        pc.select(
            COLOR_SCHEMES,
            placeholder="Select a color scheme",
            value=State.color_scheme,
            on_change=State.set_color_scheme,
        ),
        gap=4,
    )


def system():
    return pc.vstack(
        pc.button("Button", color_scheme=State.color_scheme, color="#fff"),
        pc.checkbox(
            "Checkbox", size="md", is_checked=True, color_scheme=State.color_scheme
        ),
        pc.radio("Radio", size="md", is_checked=True, color_scheme=State.color_scheme),
        pc.badge("Badge", color_scheme=State.color_scheme),
        pc.progress(
            is_indeterminate=True, width="100%", color_scheme=State.color_scheme
        ),
        pc.slider(value=50, color_scheme=State.color_scheme),
        pc.table_container(
            pc.table(
                headers=["Name", "Age", "Location"],
                rows=[
                    ("John", 30, "New York"),
                    ("Jane", 31, "San Francisco"),
                    ("Joe", 32, "Los Angeles"),
                ],
                footers=["Footer 1", "Footer 2", "Footer 3"],
                variant="striped",
                color_scheme=State.color_scheme,
            )
        ),
        pc.switch(color_scheme=State.color_scheme, is_checked=True),
        align_items="flex-start",
        gap=4,
    )


def index() -> pc.Component:
    """The index page."""
    return pc.box(
        pc.heading(
            "Theming",
            size="xl",
            letter_spacing="-1px",
            mb=8,
        ),
        theme_selector(),
        pc.switch("Dark mode", on_change=pc.toggle_color_mode, mt=4),
        pc.divider(my=12),
        system(),
        max_width="xl",
        mx="auto",
        py=8,
    )


# Add state and page to the app.
app = pc.App(state=State, stylesheets=["/globals.css"])
app.add_page(index)
app.compile()
