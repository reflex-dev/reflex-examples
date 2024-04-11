"""Miscellaneous utility functions."""

import reflex as rx


def quoted_var(value: str) -> rx.Var:
    """Allows a bare string to be used in a page title with other Vars."""
    return rx.Var.create(f"'{value}'", _var_is_local=True)
