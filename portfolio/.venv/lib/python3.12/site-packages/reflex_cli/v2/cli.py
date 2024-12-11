"""CLI for the hosting service."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Any, Callable, Optional

import httpx
import typer
from typing_extensions import Annotated

from reflex_cli import constants
from reflex_cli.utils import console
from reflex_cli.utils.dependency import extract_domain


def login(
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
) -> dict[str, Any]:
    """Authenticate with Reflex hosting service.

    Args:
        loglevel: The log level to use.

    Returns:
        Information about the logged in user.

    Raises:
        SystemExit: If the command fails.
    """
    from reflex_cli.utils import hosting

    # Set the log level.
    console.set_log_level(loglevel)

    access_token, validated_info = hosting.authenticated_token()
    if access_token:
        console.print("You already logged in.")
        return validated_info

    # If not already logged in, open a browser window/tab to the login page.
    access_token, validated_info = hosting.authenticate_on_browser()

    if not access_token:
        console.error(f"Unable to authenticate. Please try again or contact support.")
        raise SystemExit(1)

    console.print("Successfully logged in.")
    return validated_info


def logout(
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
):
    """Log out of access to Reflex hosting service.

    Args:
        loglevel: The log level to use.
    """
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    console.debug("Deleting access token from config locally")
    hosting.delete_token_from_config()
    console.success("Successfully logged out.")


def deploy(
    app_name: str,
    export_fn: Callable[[str, str, str, bool, bool, bool], None],
    description: str | None = None,
    regions: list[str] | None = None,
    project: str | None = None,
    envs: list[str] | None = None,
    vmtype: str | None = None,
    hostname: str | None = None,
    interactive: bool = True,
    envfile: str | None = None,
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    token: Optional[str] = None,
    **kwargs,
):
    """Deploy the app to the Reflex hosting service.

    Args:
        app_name (str): The name of the app.
        export_fn (Callable[[str, str, str, bool, bool, bool], None]): The function from the Reflex main framework to export the app.
        description (str | None): The app's description.
        regions (list[str] | None): The regions to deploy to.
        project (str | None): The project to deploy to.
        envs (list[str] | None): The environment variables to set.
        vmtype (str | None): The VM type to allocate.
        hostname (str | None): The hostname to use for the frontend.
        interactive (bool): Whether to use interactive mode.
        envfile (str | None): The path to an env file to use. Will override any envs set manually.
        loglevel (str): The log level to use.
        token (Optional[str]): The authentication token.
        **kwargs: Additional keyword arguments.

    Raises:
        SystemExit: If the command fails.
    """
    from reflex_cli.utils import hosting

    # Set the log level.
    console.set_log_level(loglevel)

    try:
        # check if provided project exists.
        if project:
            hosting.get_project(project, token=token)
        else:
            project = hosting.get_selected_project()
    except httpx.HTTPStatusError as ex:
        try:
            console.error(ex.response.json().get("detail"))
        except json.JSONDecodeError:
            console.error(ex.response.text)
        raise typer.Exit(1) from ex

    envs = envs or []

    if not interactive and not app_name:
        console.error(
            "Please provide a name for the deployed instance when not in interactive mode."
        )
        raise SystemExit(1)

    if len(app_name or "") > 15:
        console.error("The app name must be 15 characters or less.")
        raise SystemExit(1)

    app = hosting.search_app(app_name=app_name, project_id=project, token=token)

    if not app and interactive:
        if (
            console.ask(
                f"No app with {app_name} found. Do you want to create a new app to deploy?",
                choices=["y", "n"],
                default="y",
            )
            == "y"
        ):
            if description is None:
                description = console.ask(
                    f"App Description (Enter to skip)",
                )
            app = hosting.create_app(
                app_name=app_name,
                description=description,
                project_id=project,
                token=token,
            )
            console.info(f"created app. \nName: {app['name']} \nId: {app['id']}")
        else:
            console.error("Please create an app to deploy.")
            raise SystemExit(1)
    elif not app:
        app = hosting.create_app(
            app_name=app_name,
            description="",
            project_id=project,
            token=token,
        )
        console.info(f"created app. \nName: {app['name']} \nId: {app['id']}")

    urls = hosting.get_hostname(
        app_id=app["id"], app_name=app["name"], hostname=hostname, token=token
    )
    if "error" in urls:
        console.error(urls["error"])
        raise SystemExit(1)
    server_url = urls["server"]  # backend
    host_url = urls["hostname"]  # frontend
    processed_envs = hosting.process_envs(envs) if envs else None

    # validation_message = hosting.validate_deployment_args(
    #     app_name, project, regions, vmtype, hostname, token
    # )

    # if validation_message != "success":
    #     console.error(validation_message)
    #     raise SystemExit(1)

    if envfile:
        try:
            from dotenv import dotenv_values  # type: ignore

            processed_envs = dotenv_values(envfile)
        except ImportError:
            console.error(
                """The `python-dotenv` package is required to load environment variables from a file. Run `pip install "python-dotenv>=1.0.1"`."""
            )

    # Compile the app in production mode: backend first then frontend.
    tmp_dir = tempfile.mkdtemp()

    # Try zipping backend first
    try:
        export_fn(tmp_dir, server_url, host_url, False, True, True)
    except Exception as ex:
        console.error(f"Unable to export due to: {ex}")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise SystemExit(1) from ex

    # Zip frontend
    try:
        export_fn(tmp_dir, server_url, host_url, True, False, True)
    except ImportError as ie:
        console.error(
            f"Encountered ImportError, did you install all the dependencies? {ie}"
        )
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise SystemExit(1) from ie
    except Exception as ex:
        console.error(f"Unable to export due to: {ex}")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise SystemExit(1) from ex

    result = hosting.create_deployment(
        app_name=app_name,
        project_id=project,
        regions=regions,
        zip_dir=tmp_dir,
        hostname=extract_domain(host_url) if hostname else None,
        vmtype=vmtype,
        secrets=processed_envs,
        token=token,
    )
    if "failed" in result:
        console.error(result)
        raise SystemExit(1)
    console.print(
        f"you are now safe to exit this command.\nfollow along with the deployment with the following command: \n  reflex cloud apps status {result} --watch"
    )
    hosting.watch_deployment_status(result, token=token)
