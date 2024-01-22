"""Login page. Uses auth_layout to render UI shared with the sign up page."""
import reflex as rx
import reflex.components.radix.themes as rdxt
from twitter_radix.layouts import auth_layout
from twitter_radix.state.auth import AuthState


def login():
    """The login page."""
    return auth_layout(
        rdxt.box(
            rx.input(placeholder="Username", on_blur=AuthState.set_username, mb=4),
            rx.input(
                type_="password",
                placeholder="Password",
                on_blur=AuthState.set_password,
                mb=4,
            ),
            rdxt.button(
                "Log in",
                on_click=AuthState.login,
                color="white",
                size="3",
            ),
            align_items="left",
            bg="white",
            border="1px solid #eaeaea",
            p="4",
            max_width="400px",
            border_radius="lg",
        ),
        rdxt.text(
            "Don't have an account yet? ",
            rdxt.link("Sign up here.", href="/signup"),
            color="gray",
        ),
    )
