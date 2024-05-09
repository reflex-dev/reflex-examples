"""Miscellaneous utility functions."""

import reflex as rx

from reflex_local_auth import LoginState


def quoted_var(value: str) -> rx.Var:
    """Allows a bare string to be used in a page title with other Vars."""
    return rx.Var.create(f"'{value}'", _var_is_local=True)


def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Decorator to require authentication before rendering a page.

    If the user is not authenticated, then redirect to the login page.

    Args:
        page: The page to wrap.

    Returns:
        The wrapped page component.
    """

    def protected_page():
        return rx.cond(
            LoginState.is_authenticated,
            page(),
            rx.spinner(on_mount=LoginState.redir),
        )

    protected_page.__name__ = page.__name__
    return protected_page