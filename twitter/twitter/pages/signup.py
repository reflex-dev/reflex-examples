import pynecone as pc
from twitter.auth import AuthState, State
from twitter.layouts import auth_layout


def signup():
    return auth_layout(
        pc.box(
            pc.input(placeholder="Username", on_blur=State.set_username, mb=4),
            pc.input(placeholder="Password", on_blur=AuthState.set_password, mb=4),
            pc.input(
                placeholder="Confirm password",
                on_blur=AuthState.set_confirm_password,
                mb=4,
            ),
            pc.button(
                "Sign up",
                on_click=AuthState.signup,
                bg="blue.500",
                color="white",
                _hover={"bg": "blue.600"},
            ),
            align_items="left",
            bg="white",
            border="1px solid #eaeaea",
            p=4,
            max_width="400px",
            border_radius="lg",
        ),
        pc.text(
            "Already have an account? ",
            pc.link("Sign in here.", href="/", color="blue.500"),
            color="gray.600",
        ),
    )
