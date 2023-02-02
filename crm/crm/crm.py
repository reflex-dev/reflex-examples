"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
from pcconfig import config

import pynecone as pc
from typing import Optional


class User(pc.Model, table=True):
    name: str = "Fez"
    email: str
    password: str


class State(pc.State):
    """The app state."""

    user: Optional[User] = None


class LoginState(State):
    """State for the login form."""

    email_field: str = ""
    password_field: str = ""

    def log_in(self):
        with pc.session() as sess:
            user = sess.exec(User.select.where(User.email == self.email_field)).first()
            if user and user.password == self.password_field:
                self.user = user
                return pc.redirect("/")
            else:
                return pc.window_alert("Wrong username or password.")

    def sign_up(self):
        with pc.session() as sess:
            user = sess.exec(User.select.where(User.email == self.email_field)).first()
            if user:
                return pc.window_alert(
                    "Looks like you’re already registered! Try logging in instead."
                )
            else:
                sess.expire_on_commit = False  # Make sure the user object is accessible. https://sqlalche.me/e/14/bhk3
                user = User(email=self.email_field, password=self.password_field)
                self.user = user
                sess.add(user)
                sess.commit()
                return pc.redirect("/")

    def log_out(self):
        self.user = None
        return pc.redirect("/")


def crm():
    return pc.box(
        pc.hstack(
            pc.heading(f"Welcome, {State.user.name}."),
            pc.input(type_="text", placeholder="Filter by name", max_width="300px"),
            justify_content="space-between",
        ),
        pc.box(border_radius="8px", border="1px solid #eaeaef"),
        width="100%",
        max_width="960px",
    )


def index():
    return pc.vstack(
        navbar(),
        pc.cond(
            State.user,
            crm(),
            pc.vstack(
                pc.heading("Welcome to Pyneknown!"),
                pc.text(
                    "This Pynecone example demonstrates how to build a fully-fledged customer relationship management (CRM) interface."
                ),
                pc.link(
                    pc.button(
                        "Log in to get started", color_scheme="blue", underline="none"
                    ),
                    href="/login",
                ),
                max_width="500px",
                text_align="center",
                spacing="1rem",
            ),
        ),
        spacing="1.5rem",
    )


def navbar():
    return pc.box(
        pc.hstack(
            pc.link("Pyneknown", href="/", font_weight="medium"),
            pc.hstack(
                pc.cond(
                    State.user,
                    pc.hstack(
                        pc.link(
                            "Log out",
                            color="blue.600",
                            on_click=LoginState.log_out,
                        ),
                        pc.avatar(name=State.user.email, size="md"),
                        spacing="1rem",
                    ),
                    pc.box(),
                )
            ),
            justify_content="space-between",
        ),
        width="100%",
        padding="1rem",
        margin_bottom="2rem",
        border_bottom="1px solid black",
    )


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


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.add_page(login)
app.compile()
