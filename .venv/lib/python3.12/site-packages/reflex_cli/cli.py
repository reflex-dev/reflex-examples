"""CLI for the hosting service."""

from __future__ import annotations

import os
import shutil
import tempfile
from datetime import datetime
from typing import Callable

from reflex_cli import constants
from reflex_cli.utils import console


def login(
    loglevel: str = constants.LogLevel.INFO.value,
):
    """Authenticate with Reflex hosting service.

    Args:
        loglevel: The log level to use.

    Raises:
        SystemExit: If the command fails.
    """
    from reflex_cli.utils import hosting

    # Set the log level.
    console.set_log_level(constants.LogLevel(loglevel))

    access_token, invitation_code = hosting.authenticated_token()
    if access_token:
        console.print("You already logged in.")
        return

    # If not already logged in, open a browser window/tab to the login page.
    access_token = hosting.authenticate_on_browser(invitation_code)

    if not access_token:
        console.error(f"Unable to authenticate. Please try again or contact support.")
        raise SystemExit(1)

    console.print("Successfully logged in.")


def logout(
    loglevel: str = constants.LogLevel.INFO.value,
):
    """Log out of access to Reflex hosting service.

    Args:
        loglevel: The log level to use.
    """
    from reflex_cli.utils import hosting

    console.set_log_level(constants.LogLevel(loglevel))

    hosting.log_out_on_browser()
    console.debug("Deleting access token from config locally")
    hosting.delete_token_from_config(include_invitation_code=True)


def deploy(
    app_name: str,
    export_fn: Callable[[str, str, str, bool, bool, bool], None],
    regions: list[str] | None = None,
    key: str | None = None,
    envs: list[str] | None = None,
    cpus: int | None = None,
    memory_mb: int | None = None,
    auto_start: bool | None = None,
    auto_stop: bool | None = None,
    frontend_hostname: str | None = None,
    interactive: bool = True,
    with_metrics: str | None = None,
    with_tracing: str | None = None,
    share_deployment: bool | None = None,
    loglevel: str = constants.LogLevel.INFO.value,
):
    """Deploy the app to the Reflex hosting service.

    Args:
        app_name: The name of the app.
        export_fn: The function from the reflex main framework to export the app.
        regions: The regions to deploy to.
        key: The deployment key.
        envs: The environment variables to set.
        cpus: The number of CPUs to allocate.
        memory_mb: The amount of memory to allocate in MB.
        auto_start: Whether to automatically start the deployment.
        auto_stop: Whether to automatically stop the deployment.
        frontend_hostname: The hostname to use for the frontend.
        interactive: Whether to use interactive mode.
        with_metrics: The metrics prefix to use if enabling metrics.
        with_tracing: The tracing prefix to use if enabling tracing.
        share_deployment: Whether to share the deployment. If None, prompt the user when in interactive mode.
        loglevel: The log level to use.

    Raises:
        SystemExit: If the command fails.
    """
    from reflex_cli.utils import hosting

    # Set the log level.
    console.set_log_level(constants.LogLevel(loglevel))

    envs = envs or []
    api_url = ""
    deploy_url = ""

    if not interactive and not key:
        console.error(
            "Please provide a name for the deployed instance when not in interactive mode."
        )
        raise SystemExit(1)

    if interactive and share_deployment is None:
        if (
            console.ask(
                "Do you want to share your app in the Gallery?",
                choices=["y", "n"],
                default="y",
            )
            == "y"
        ):
            share_deployment = True
            console.print(
                "We will ask for more information later. Let's proceed to deploy."
            )
        else:
            share_deployment = False
            console.print(
                "No worries. You can do this later by running `reflex deployments share`."
            )

    enabled_regions = None
    # If there is already a key, then it is passed in from CLI option in the non-interactive mode
    if key is not None and not hosting.is_valid_deployment_key(key):
        console.error(
            f"Deployment key {key} is not valid. Please use only domain name safe characters."
        )
        raise SystemExit(1)
    try:
        # Send a request to server to obtain necessary information
        # in preparation of a deployment. For example,
        # server can return confirmation of a particular deployment key,
        # is available, or suggest a new key, or return an existing deployment.
        # Some of these are used in the interactive mode.
        pre_deploy_response = hosting.prepare_deploy(
            app_name, key=key, frontend_hostname=frontend_hostname
        )
        # Note: we likely won't need to fetch this twice
        if pre_deploy_response.enabled_regions is not None:
            enabled_regions = pre_deploy_response.enabled_regions

    except Exception as ex:
        console.error(f"Unable to prepare deployment")
        raise SystemExit(1) from ex

    # The app prefix should not change during the time of preparation
    app_prefix = pre_deploy_response.app_prefix
    if not interactive:
        # in this case, the key was supplied for the pre_deploy call, at this point the reply is expected
        if (reply := pre_deploy_response.reply) is None:
            console.error(f"Unable to deploy at this name {key}.")
            raise SystemExit(1)
        api_url = reply.api_url
        deploy_url = reply.deploy_url
    else:
        (
            key_candidate,
            api_url,
            deploy_url,
        ) = hosting.interactive_get_deployment_key_from_user_input(
            pre_deploy_response, app_name, frontend_hostname=frontend_hostname
        )
        if not key_candidate or not api_url or not deploy_url:
            console.error("Unable to find a suitable deployment key.")
            raise SystemExit(1)

        # Now copy over the candidate to the key
        key = key_candidate

        regions = hosting.prompt_for_regions(
            enabled_regions=enabled_regions, regions_args=regions
        )

        # process the envs
        envs = hosting.interactive_prompt_for_envs()

    # Check the required params are valid
    console.debug(
        f"{key=}, {regions=}, {app_name=}, {app_prefix=}, {api_url=}, {deploy_url=}"
    )
    if (
        not key
        or not regions
        or not app_name
        or not app_prefix
        or not api_url
        or not deploy_url
    ):
        console.error("Please provide all the required parameters.")
        raise SystemExit(1)
    # Note: if the user uses --no-interactive mode, there was no prepare_deploy call
    # so we do not check the regions until the call to hosting server

    processed_envs = hosting.process_envs(envs) if envs else None

    # Compile the app in production mode: backend first then frontend.
    tmp_dir = tempfile.mkdtemp()

    # Try zipping backend first
    try:
        export_fn(tmp_dir, api_url, deploy_url, False, True, True)
    except Exception as ex:
        console.error(f"Unable to export due to: {ex}")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise SystemExit(1) from ex

    backend_file_name = constants.ComponentName.BACKEND.zip()

    console.print("Uploading Backend code and sending request ...")
    backend_deploy_requested_at = datetime.now().astimezone()
    console.debug(f"{backend_deploy_requested_at=}")
    try:
        backend_deploy_response = hosting.deploy_backend(
            backend_file_name=backend_file_name,
            export_dir=tmp_dir,
            key=key,
            app_name=app_name,
            regions=regions,
            app_prefix=app_prefix,
            cpus=cpus,
            memory_mb=memory_mb,
            auto_start=auto_start,
            auto_stop=auto_stop,
            envs=processed_envs,
            with_metrics=with_metrics,
            with_tracing=with_tracing,
        )
    except Exception as ex:
        console.error(f"Unable to deploy due to: {ex}")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise SystemExit(1) from ex

    if backend_deploy_response.sidecar_url is None:
        console.error(
            "Deploy backend response from server missing sidecar_url. This is unexpected. Contact support."
        )
        raise SystemExit(1)

    # Deployment will actually start when data plane reconciles this request
    console.debug(f"deploy_response: {backend_deploy_response}")
    console.print("[bold]Backend deployment will start shortly.")

    # Zip frontend
    try:
        export_fn(tmp_dir, api_url, deploy_url, True, False, True)
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

    frontend_file_name = constants.ComponentName.FRONTEND.zip()

    console.print("Uploading Frontend code and sending request ...")
    frontend_deploy_requested_at = datetime.now().astimezone()
    console.debug(f"{frontend_deploy_requested_at=}")
    try:
        frontend_deploy_response = hosting.deploy_frontend(
            frontend_file_name=frontend_file_name,
            export_dir=tmp_dir,
            initiator_event_id=backend_deploy_response.event_id,
            app_prefix=app_prefix,
            frontend_hostname=frontend_hostname,
        )
    except Exception as ex:
        console.error(f"Unable to deploy due to: {ex}")
        raise SystemExit(1) from ex
    finally:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
    console.debug(f"deploy_response: {frontend_deploy_response}")
    console.print("[bold]Frontend deployment will start shortly.")

    console.rule("[bold]Deploying production app.")
    console.print(
        f"[bold]Deployment will start shortly: {frontend_deploy_response.url} \nClosing this command now will not affect your deployment."
    )

    # If user elected to share the deployment, instead of just waiting, collect information from them.
    if share_deployment:
        hosting.collect_deployment_info_interactive(
            demo_url=frontend_deploy_response.url
        )
    else:
        # It takes a few seconds for the deployment request to be picked up by server
        hosting.wait_for_server_to_pick_up_request()

    console.print("Waiting for server to report progress ...")
    # Display the key events such as build, deploy, etc based on the deploy event IDs from hosting service
    server_report_deploy_success = hosting.poll_deploy_milestones(
        key,
        from_iso_timestamp=backend_deploy_requested_at,
        deploy_event_ids=[
            backend_deploy_response.event_id,
            frontend_deploy_response.event_id,
        ],
    )

    if server_report_deploy_success is None:
        console.warn("The deployment may still be in progress. Proceeding ...")
    elif not server_report_deploy_success:
        console.error("Hosting server reports failure.")
        console.error(
            f"Check for more server logs using `reflex deployments build-logs {key}`"
        )
        raise SystemExit(1)

    console.print("Waiting for the new deployment to come up")
    backend_reachable, backend_poll_err = hosting.poll_backend_with_retries(
        key=key,
        from_iso_timestamp=datetime.now().astimezone(),
        backend_url=backend_deploy_response.url,
        sidecar_url=backend_deploy_response.sidecar_url,
    )
    if not backend_reachable:
        if backend_poll_err is not None:
            print(backend_poll_err)
        console.error("Backend unreachable")
        console.warn(
            f"Check for more logs in your App, using `reflex deployments logs {key}`"
        )
        raise SystemExit(1)

    if not (
        frontend_reachable := hosting.poll_frontend_with_retries(
            frontend_url=frontend_deploy_response.url
        )
    ):
        console.error("Frontend unreachable")
        raise SystemExit(1)

    if backend_reachable and frontend_reachable:
        console.print(
            f"Your site [ {key} ] at {regions} is up: {frontend_deploy_response.url}"
        )
        return
    console.warn(f"Your deployment is taking unusually long.")
    console.warn(f"Check back later on its status: `reflex deployments status {key}`")
    console.warn(f"For logs: `reflex deployments logs {key}`")
