from crm.state import LoginState
from crm.components import navbar
import reflex as rx


def login():
    return rx.chakra.vstack(
        navbar(),
        rx.chakra.box(
            rx.chakra.heading("Log in", margin_bottom="1rem"),
            rx.chakra.input(
                type_="email",
                placeholder="Email",
                margin_bottom="1rem",
                on_change=LoginState.set_email_field,
            ),
            rx.chakra.input(
                type_="password",
                placeholder="Password",
                margin_bottom="1rem",
                on_change=LoginState.set_password_field,
            ),
            rx.chakra.button("Log in", on_click=LoginState.log_in),
            rx.chakra.box(
                rx.chakra.link(
                    "Or sign up with this email and password",
                    href="#",
                    on_click=LoginState.sign_up,
                ),
                margin_top="0.5rem",
            ),
            max_width="350px",
            flex_direction="column",
        ),
    )
