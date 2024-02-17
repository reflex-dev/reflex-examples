"""New user registration form and validation logic."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import reflex as rx

from sqlmodel import select

from .base_state import State
from .login import LOGIN_ROUTE, REGISTER_ROUTE
from .user import User


class RegistrationState(State):
    """Handle registration form submission and redirect to login page after registration."""

    success: bool = False
    error_message: str = ""

    async def handle_registration(
        self, form_data
    ) -> AsyncGenerator[rx.event.EventSpec | list[rx.event.EventSpec] | None, None]:
        """Handle registration form on_submit.

        Set error_message appropriately based on validation results.

        Args:
            form_data: A dict of form fields and values.
        """
        with rx.session() as session:
            username = form_data["username"]
            if not username:
                self.error_message = "Username cannot be empty"
                yield rx.set_focus("username")
                return
            existing_user = session.exec(
                select(User).where(User.username == username)
            ).one_or_none()
            if existing_user is not None:
                self.error_message = (
                    f"Username {username} is already registered. Try a different name"
                )
                yield [rx.set_value("username", ""), rx.set_focus("username")]
                return
            password = form_data["password"]
            if not password:
                self.error_message = "Password cannot be empty"
                yield rx.set_focus("password")
                return
            if password != form_data["confirm_password"]:
                self.error_message = "Passwords do not match"
                yield [
                    rx.set_value("confirm_password", ""),
                    rx.set_focus("confirm_password"),
                ]
                return
            # Create the new user and add it to the database.
            new_user = User()  # type: ignore
            new_user.username = username
            new_user.password_hash = User.hash_password(password)
            new_user.enabled = True
            session.add(new_user)
            session.commit()
        # Set success and redirect to login page after a brief delay.
        self.error_message = ""
        self.success = True
        yield
        await asyncio.sleep(0.5)
        yield [rx.redirect(LOGIN_ROUTE), RegistrationState.set_success(False)]


@rx.page(route=REGISTER_ROUTE)
def registration_page() -> rx.Component:
    """Render the registration page.

    Returns:
        A reflex component.
    """

    register_form = rx.box(
        rx.vstack(
            rx.form(
                rx.fragment(
                    rx.heading("Create an account", size="7", margin_bottom="2rem"),
                    rx.text(
                        "Username",
                        color="hsl(240, 5%, 64.9%)",
                        margin_top="2px",
                        margin_bottom="4px",
                    ),
                    rx.input(
                        placeholder="username",
                        id="username",
                        border_color="hsl(240,3.7%,15.9%)",
                        justify_content="center",
                    ),
                    rx.text(
                        "Password",
                        color="hsl(240, 5%, 64.9%)",
                        margin_top="2px",
                        margin_bottom="4px",
                    ),
                    rx.input(
                        placeholder="password",
                        id="password",
                        border_color="hsl(240,3.7%,15.9%)",
                        justify_content="center",
                        type="password",
                    ),
                    rx.text(
                        "Confirm Password",
                        color="hsl(240, 5%, 64.9%)",
                        margin_top="2px",
                        margin_bottom="4px",
                    ),
                    rx.input(
                        placeholder="confirm",
                        id="confirm_password",
                        border_color="hsl(240,3.7%,15.9%)",
                        justify_content="center",
                        type="password",
                    ),
                    rx.box(
                        rx.button(
                            "Sign up",
                            type="submit",
                            width="100%",
                        ),
                        padding_top="14px",
                    ),
                ),
                on_submit=RegistrationState.handle_registration,
            ),
            rx.link("Login", href=LOGIN_ROUTE),
            align_items="center"
        ),
        padding="8rem 10rem",
        margin_top="10vh",
        margin_x="auto",
        border="2px solid black",
        border_color="gray.300",
        border_radius=10,
    )

    return rx.fragment(
        rx.cond(
            RegistrationState.success,
            rx.vstack(
                rx.text("Registration successful!"),
                rx.chakra.spinner(),
            ),
            rx.vstack(
                rx.cond(  # conditionally show error messages
                    RegistrationState.error_message != "",
                    rx.callout(
                        RegistrationState.error_message,
                        icon="alert_triangle",
                        color_scheme="red",
                        role="alert",
                    ),
                ),
                register_form,
                padding_top="10vh",
            ),
        )
    )