from crm.state import LoginState
from crm.components import navbar
import reflex as rx
import reflex.components.radix.themes as rdxt


def login():
    return rx.vstack(
        navbar(),
        rdxt.box(
            rdxt.heading("Log in", margin_bottom="1rem"),
            rdxt.textfield_root(
                rdxt.textfield_input(
                    type_="email",
                    placeholder="Email",
                    on_change=LoginState.set_email_field,
                ),
                margin_bottom="1rem",
            ),
            rdxt.textfield_root(
                rdxt.textfield_input(
                    type_="password",
                    placeholder="Password",
                    on_change=LoginState.set_password_field,
                ),
                margin_bottom="1rem",
            ),
            rdxt.button("Log in", on_click=LoginState.log_in),
            rdxt.box(
                rdxt.link(
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
