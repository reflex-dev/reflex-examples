"""Login page and authentication logic."""
import reflex as rx
from sqlmodel import select

from .base_state import State
from .user import User


LOGIN_ROUTE = "/login"
REGISTER_ROUTE = "/register"


class LoginState(State):
    """Handle login form submission and redirect to proper routes after authentication."""

    error_message: str = ""
    redirect_to: str = ""

    def on_submit(self, form_data) -> rx.event.EventSpec:
        """Handle login form on_submit.

        Args:
            form_data: A dict of form fields and values.
        """
        self.error_message = ""
        username = form_data["username"]
        password = form_data["password"]
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.username == username)
            ).one_or_none()
        if user is not None and not user.enabled:
            self.error_message = "This account is disabled."
            return rx.set_value("password", "")
        if user is None or not user.verify(password):
            self.error_message = "There was a problem logging in, please try again."
            return rx.set_value("password", "")
        if (
            user is not None
            and user.id is not None
            and user.enabled
            and user.verify(password)
        ):
            # mark the user as logged in
            self._login(user.id)
        self.error_message = ""
        return LoginState.redir()  # type: ignore

    def redir(self) -> rx.event.EventSpec | None:
        """Redirect to the redirect_to route if logged in, or to the login page if not."""
        if not self.is_hydrated:
            # wait until after hydration to ensure auth_token is known
            return LoginState.redir()  # type: ignore
        page = self.router.page.path
        if not self.is_authenticated and page != LOGIN_ROUTE:
            self.redirect_to = page
            return rx.redirect(LOGIN_ROUTE)
        elif page == LOGIN_ROUTE:
            return rx.redirect(self.redirect_to or "/")


@rx.page(route=LOGIN_ROUTE)
def login_page() -> rx.Component:
    """Render the login page.

    Returns:
        A reflex component.
    """

    login_form = rx.box(
        rx.vstack(
            rx.form(
                rx.fragment(
                    rx.heading(
                        "Login into your Account", size="7", margin_bottom="2rem"
                    ),
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
                    rx.box(
                        rx.button(
                            "Sign in",
                            type="submit",
                            width="100%",
                        ),
                        padding_top="14px",
                    ),
                ),
                on_submit=LoginState.on_submit,
            ),
            rx.link("Register", href=REGISTER_ROUTE),
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
            LoginState.is_hydrated,  # type: ignore
            rx.vstack(
                rx.cond(  # conditionally show error messages
                    LoginState.error_message != "",
                    rx.callout(
                        LoginState.error_message,
                        icon="alert_triangle",
                        color_scheme="red",
                        role="alert",
                    ),
                ),
                login_form,
                padding_top="10vh",
            ),
        )
    )


def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Decorator to require authentication before rendering a page.

    If the user is not authenticated, then redirect to the login page.

    Args:
        page: The page to wrap.

    Returns:
        The wrapped page component.
    """

    def protected_page():
        return rx.fragment(
            rx.cond(
                State.is_hydrated & State.is_authenticated,  # type: ignore
                page(),
                rx.center(
                    # When this spinner mounts, it will redirect to the login page
                    rx.chakra.spinner(on_mount=LoginState.redir),
                ),
            )
        )

    protected_page.__name__ = page.__name__
    return protected_page