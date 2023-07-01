from crm.state import LoginState
from crm.components import navbar
import reflex as rx


def login():
    return rx.vstack(
        navbar(),
        rx.box(
            rx.heading("Log in", margin_bottom="1rem"),
            rx.input(
                type_="email",
                placeholder="Email",
                margin_bottom="1rem",
                on_change=LoginState.set_email_field,
            ),
            rx.input(
                type_="password",
                placeholder="Password",
                margin_bottom="1rem",
                on_change=LoginState.set_password_field,
            ),
            rx.button("Log in", on_click=LoginState.log_in),
            rx.box(
                rx.link(
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
