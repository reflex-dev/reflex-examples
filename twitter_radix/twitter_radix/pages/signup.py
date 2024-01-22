"""Sign up page. Uses auth_layout to render UI shared with the login page."""
import reflex as rx
import reflex.components.radix.themes as rdxt
from twitter_radix.layouts import auth_layout
from twitter_radix.state.auth import AuthState


def signup():
    """The sign up page."""
    return auth_layout(
        rdxt.box(
            rx.input(placeholder="Username", on_blur=AuthState.set_username, mb=4),
            rx.input(
                type_="password",
                placeholder="Password",
                on_blur=AuthState.set_password,
                mb=4,
            ),
            rx.input(
                type_="password",
                placeholder="Confirm password",
                on_blur=AuthState.set_confirm_password,
                mb=4,
            ),
            rdxt.button(
                "Sign up",
                on_click=AuthState.signup,
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
            "Already have an account? ",
            rdxt.link("Sign in here.", href="/"),
            color="gray",
        ),
    )
