"""Reflex utilities."""

import typer

from . import console


def disabled_v1_hosting(*args, **kwargs):
    """Print error and exit when using v1 hosting commands.

    Args:
        *args: ignored.
        **kwargs: ignored.

    Raises:
        Exit: Always.
    """
    console.error(
        "The alpha hosting service has been decommissioned as of Dec 5, 2024. "
        "Please upgrade to reflex>=0.6.6.post1 to use Reflex Cloud hosting."
    )
    raise typer.Exit(1)
