from crm.state import LoginState
from crm.components import navbar
import pynecone as pc


def login():
    return pc.vstack(
        navbar(),
        pc.box(
            pc.heading("Log in", margin_bottom="1rem"),
            pc.input(
                type_="email",
                placeholder="Email",
                margin_bottom="1rem",
                on_change=LoginState.set_email_field,
            ),
            pc.input(
                type_="password",
                placeholder="Password",
                margin_bottom="1rem",
                on_change=LoginState.set_password_field,
            ),
            pc.button("Log in", on_click=LoginState.log_in),
            pc.box(
                pc.link(
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
