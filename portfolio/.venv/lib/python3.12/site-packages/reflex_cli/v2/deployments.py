"""The Hosting CLI deployments sub-commands."""

import importlib.metadata

import httpx
import typer
from packaging import version

from reflex_cli import constants
from reflex_cli.utils import console
from reflex_cli.v2.apps import apps_cli
from reflex_cli.v2.project import project_cli
from reflex_cli.v2.secrets import secrets_cli
from reflex_cli.v2.vmtypes_regions import vm_types_regions_cli

hosting_cli = typer.Typer()

hosting_cli.add_typer(
    apps_cli,
    name="apps",
    help="Subcommands for managing the reflex cloud apps.",
)
hosting_cli.add_typer(
    project_cli,
    name="project",
    help="Subcommands for managing the reflex cloud project.",
)
hosting_cli.add_typer(
    secrets_cli,
    name="secrets",
    help="Subcommands for managing the reflex cloud secrets.",
)
hosting_cli.add_typer(
    vm_types_regions_cli,
    name="",
    help="Subcommands for VM types and available regions.",
)


TIME_FORMAT_HELP = "Accepts ISO 8601 format, unix epoch or time relative to now. For time relative to now, use the format: <d><unit>. Valid units are d (day), h (hour), m (minute), s (second). For example, 1d for 1 day ago from now."
MIN_LOGS_LIMIT = 50
MAX_LOGS_LIMIT = 1000


@hosting_cli.callback()
def check_version():
    """Callback to be invoked for all hosting CLI commands.

    Checks if the installed version of the package is up-to-date with the latest version available on PyPI.
    If a newer version is available, it prints a warning message and exits.

    Raises:
        Exit: If a newer version is available, prompting the user to upgrade.
    """
    package_name = constants.ReflexHostingCli.MODULE_NAME
    try:
        installed_version = importlib.metadata.version(package_name)
        response = httpx.get(f"https://pypi.org/pypi/{package_name}/json")
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        if version.parse(installed_version) < version.parse(latest_version):
            print(
                f"Warning: You are using {package_name} version {installed_version}. "
                f"A newer version {latest_version} is available."
            )
            console.error(f"Upgrade using: pip install --upgrade {package_name}")
            raise typer.Exit(1)
    except (
        importlib.metadata.PackageNotFoundError,
        httpx.RequestError,
        httpx.HTTPStatusError,
    ):
        # Silently pass if we can't check the version
        pass
