"""Shared auth layout."""
import reflex as rx
import reflex.components.radix.themes as rdxt

from ..components import container


def auth_layout(*args):
    """The shared layout for the login and sign up pages."""
    return rdxt.box(
        container(
            rx.heading(
                rx.span("Welcome to PySocial!"),
                rx.span("Sign in or sign up to get started."),
                display="flex",
                flex_direction="column",
                align_items="center",
                text_align="center",
            ),
            rdxt.text(
                "See the source code for this demo app ",
                rdxt.link(
                    "here",
                    href="https://github.com/reflex-dev/reflex-examples/tree/main/twitter",
                ),
                ".",
                color="gray",
                font_weight="medium",
            ),
            *args,
            border_top_radius="lg",
            box_shadow="0 4px 60px 0 rgba(0, 0, 0, 0.08), 0 4px 16px 0 rgba(0, 0, 0, 0.08)",
            display="flex",
            flex_direction="column",
            align_items="center",
            py="8",
            gap="1rem",
        ),
        height="100vh",
        pt="9",
        background="url(bg.svg)",
        background_repeat="no-repeat",
        background_size="cover",
    )
