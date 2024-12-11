"""Disabled Hosting CLI deployments sub-commands."""

from typing import Optional

import typer

from reflex_cli import constants
from reflex_cli.utils import disabled_v1_hosting

deployments_cli = typer.Typer()

TIME_FORMAT_HELP = "Accepts ISO 8601 format, unix epoch or time relative to now. For time relative to now, use the format: <d><unit>. Valid units are d (day), h (hour), m (minute), s (second). For example, 1d for 1 day ago from now."
MIN_LOGS_LIMIT = 50
MAX_LOGS_LIMIT = 1000


@deployments_cli.command(name="list")
def list_deployments(
    loglevel: constants.LogLevel = typer.Option(
        constants.LogLevel.INFO, help="The log level to use."
    ),
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """List all the hosted deployments of the authenticated user.

    Args:
        loglevel: The log level to use.
        as_json: Whether to output the result in json format.
    """
    disabled_v1_hosting()


@deployments_cli.command(name="delete")
def delete_deployment(
    key: str = typer.Argument(..., help="The name of the deployment."),
    loglevel: constants.LogLevel = typer.Option(
        constants.LogLevel.INFO, help="The log level to use."
    ),
):
    """Delete a hosted instance.

    Args:
        key: The name of the deployment.
        loglevel: The log level to use.
    """
    disabled_v1_hosting()


@deployments_cli.command(name="status")
def get_deployment_status(
    key: str = typer.Argument(..., help="The name of the deployment."),
    loglevel: constants.LogLevel = typer.Option(
        constants.LogLevel.INFO, help="The log level to use."
    ),
):
    """Check the status of a deployment.

    Args:
        key: The name of the deployment.
        loglevel: The log level to use.
    """
    disabled_v1_hosting()


@deployments_cli.command(name="logs")
def get_deployment_logs(
    key: str = typer.Argument(..., help="The name of the deployment."),
    from_timestamp: Optional[str] = typer.Option(
        None,
        "--from",
        help=f"The start time of the logs. {TIME_FORMAT_HELP}",
    ),
    to_timestamp: Optional[str] = typer.Option(
        None, "--to", help=f"The end time of the logs. {TIME_FORMAT_HELP}"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        help=f"The number of logs to return. The acceptable range is {MIN_LOGS_LIMIT}-{MAX_LOGS_LIMIT}.",
    ),
    loglevel: constants.LogLevel = typer.Option(
        constants.LogLevel.INFO, help="The log level to use."
    ),
):
    """Get the logs for a deployment.

    Args:
        key: The name of the deployment.
        from_timestamp: The start time of the logs.
        to_timestamp: The end time of the logs.
        limit: The maximum number of logs to return.
        loglevel: The log level to use.
    """
    disabled_v1_hosting()


@deployments_cli.command(name="build-logs")
def get_deployment_build_logs(
    key: str = typer.Argument(..., help="The name of the deployment."),
    from_timestamp: Optional[str] = typer.Option(
        None,
        "--from",
        help=f"The start time of the logs. {TIME_FORMAT_HELP}",
    ),
    to_timestamp: Optional[str] = typer.Option(
        None, "--to", help=f"The end time of the logs. {TIME_FORMAT_HELP}"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        help=f"The number of logs to return. The acceptable range is {MIN_LOGS_LIMIT}-{MAX_LOGS_LIMIT}.",
    ),
    loglevel: constants.LogLevel = typer.Option(
        constants.LogLevel.INFO, help="The log level to use."
    ),
):
    """Get the build logs for a deployment.

    Args:
        key: The name of the deployment.
        from_timestamp: The start time of the logs.
        to_timestamp: The end time of the logs.
        limit: The maximum number of logs to return.
        loglevel: The log level to use.
    """
    disabled_v1_hosting()


@deployments_cli.command(name="regions")
def get_deployment_regions(
    loglevel: constants.LogLevel = typer.Option(
        constants.LogLevel.INFO, help="The log level to use."
    ),
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """List all the regions of the hosting service.

    Args:
        loglevel: The log level to use.
        as_json: Whether to output the result in json format.
    """
    disabled_v1_hosting()


@deployments_cli.command(name="share")
def share_deployment(
    url: Optional[str] = typer.Option(
        None,
        help="The URL of the deployed app to share. If not provided, the latest deployment is shared.",
    ),
    loglevel: constants.LogLevel = typer.Option(
        constants.LogLevel.INFO, help="The log level to use."
    ),
):
    """Share a deployment.

    Args:
        url: The URL of the deployed app to share.
        loglevel: The log level to use.
    """
    disabled_v1_hosting()
