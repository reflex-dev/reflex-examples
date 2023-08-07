import reflex as rx

from .wrappers import flex
from .components import column_one, column_two, column_three


def index() -> rx.Component:
    return flex(
        # column 1
        column_one(),
        # column 2
        column_two(),
        # column 3
        column_three(),
        h=[None, None, "100vh"],
        direction="row",
        overflow="hidden",
        max_width="2000px",
    )


# Add state and page to the app.
app = rx.App(stylesheets=["styles.css"])
app.add_page(index)
app.compile()
