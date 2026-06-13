"""Shared auth layout."""

import reflex as rx

from ..components import container


def auth_layout(*args):
    """The shared layout for the login and sign up pages."""
    return rx.box(
        container(
            rx.vstack(
                rx.heading(
                    "Welcome to PySocial!", 
                    size="8",
                    color="#16B8F3",
                    font_weight="bold",
                ),
                rx.heading(
                    "Sign in or sign up to get started.", 
                    size="6",
                    color="#14171A",
                ),
                align="center",
                spacing="2",
            ),
            rx.text(
                "See the source code for this demo app ",
                rx.link(
                    "here",
                    href="https://github.com/reflex-dev/reflex-examples/tree/main/twitter",
                    color="#16B8F3",
                    _hover={"color": "#1A91DA"},
                ),
                ".",
                color="#657786",
                font_weight="medium",
            ),
            *args,
            border_radius="16px",
            box_shadow="0 100px 60px 0 rgba(29, 161, 242, 0.1), 0 4px 16px 0 rgba(0, 0, 0, 0.12)",
            display="flex",
            flex_direction="column",
            align_items="center",
            padding_top="48px",
            padding_bottom="32px",
            spacing="5",
            background="white",
            border="1px solid #E1E8ED",
        ),
        height="100vh",
        padding_top="40px",
        background="linear-gradient(135deg, ##16B8F3 0%, #14171A 100%)",
        background_repeat="no-repeat",
        background_size="cover",
    )
