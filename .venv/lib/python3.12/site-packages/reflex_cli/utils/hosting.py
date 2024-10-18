"""Hosting service related utilities."""

from __future__ import annotations

import contextlib
import enum
import json
import os
import platform
import re
import time
import uuid
import webbrowser
from datetime import datetime, timedelta
from http import HTTPStatus
from importlib import metadata
from typing import List, Optional

import dateutil.parser
import httpx
import typer
import websockets
from pydantic import BaseModel, Field, ValidationError, root_validator

from reflex_cli import constants
from reflex_cli.utils import console
from reflex_cli.utils.dependency import detect_encoding

# Endpoint to create or update a deployment
POST_DEPLOYMENTS_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/deployments"
# Endpoint to get all deployments for the user
GET_DEPLOYMENTS_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/deployments"
# Endpoint to fetch information from backend in preparation of a deployment
POST_DEPLOYMENTS_PREPARE_ENDPOINT = (
    f"{constants.Hosting.CP_BACKEND_URL}/deployments/prepare"
)
# Endpoint to authenticate current user
POST_VALIDATE_ME_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/authenticate/me"
# Endpoint to fetch a login token after user completes authentication on web
FETCH_TOKEN_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/authenticate"
# Endpoint to delete a deployment
DELETE_DEPLOYMENTS_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/deployments"
# Endpoint to get deployment status
GET_DEPLOYMENT_STATUS_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/deployments"
# Public endpoint to get the list of supported regions in hosting service
GET_REGIONS_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/deployments/regions"
# Websocket endpoint to stream logs of a deployment
DEPLOYMENT_LOGS_ENDPOINT = (
    f'{constants.Hosting.CP_BACKEND_URL.replace("http", "ws")}/deployments'
)
# The HTTP endpoint to fetch logs of a deployment
POST_DEPLOYMENT_LOGS_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/deployments/logs"
# The HTTP endpoint to update the gallery app data.
POST_GALLERY_APPS_ENDPOINT = f"{constants.Hosting.CP_BACKEND_URL}/deployments/gallery"

# Expected server response time to new deployment request. In seconds.
DEPLOYMENT_PICKUP_DELAY = 30
# End of deployment workflow message. Used to determine if it is the last message from server.
END_OF_DEPLOYMENT_MESSAGES = ["deploy success (backend)", "deploy success (frontend)"]
# Reflex App start message in all lower cases.
REFLEX_APP_START_MESSAGE = "app running"
# Stacktrace keyword
APP_LOG_STACKTRACE_WORD = "traceback"
# Stacktrace number of message limit
APP_LOG_STACKTRACE_LINE_LIMIT = 50
# How many iterations to try and print the deployment event messages from server during deployment.
DEPLOYMENT_EVENT_MESSAGES_RETRIES = 90
# Timeout limit for http requests
HTTP_REQUEST_TIMEOUT = 60  # seconds
# Timeout limit for log query
LOG_QUERY_TIMEOUT = 10  # seconds


def get_existing_access_token() -> tuple[str, str]:
    """Fetch the access token from the existing config if applicable.

    Returns:
        The access token and the invitation code.
        If either is not found, return empty string for it instead.
    """
    console.debug("Fetching token from existing config...")
    access_token = invitation_code = ""
    try:
        with open(constants.Hosting.HOSTING_JSON, "r") as config_file:
            hosting_config = json.load(config_file)
            access_token = hosting_config.get("access_token", "")
            invitation_code = hosting_config.get("code", "")
    except Exception as ex:
        console.debug(
            f"Unable to fetch token from {constants.Hosting.HOSTING_JSON} due to: {ex}"
        )
    return access_token, invitation_code


def validate_token(token: str):
    """Validate the token with the control plane.

    Args:
        token: The access token to validate.

    Raises:
        ValueError: if access denied.
        Exception: if runs into timeout, failed requests, unexpected errors. These should be tried again.
    """
    try:
        response = httpx.post(
            POST_VALIDATE_ME_ENDPOINT,
            headers=authorization_header(token),
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise ValueError
        response.raise_for_status()
    except httpx.RequestError as re:
        console.debug(f"Request to auth server failed due to {re}")
        raise Exception(str(re)) from re
    except httpx.HTTPError as ex:
        console.debug(f"Unable to validate the token due to: {ex}")
        raise Exception("server error") from ex
    except ValueError as ve:
        console.debug(f"Access denied for {token}")
        raise ValueError("access denied") from ve
    except Exception as ex:
        console.debug(f"Unexpected error: {ex}")
        raise Exception("internal errors") from ex


def delete_token_from_config(include_invitation_code: bool = False):
    """Delete the invalid token from the config file if applicable.

    Args:
        include_invitation_code:
            Whether to delete the invitation code as well.
            When user logs out, we delete the invitation code together.
    """
    if os.path.exists(constants.Hosting.HOSTING_JSON):
        hosting_config = {}
        try:
            with open(constants.Hosting.HOSTING_JSON, "w") as config_file:
                hosting_config = json.load(config_file)
                del hosting_config["access_token"]
                if include_invitation_code:
                    del hosting_config["code"]
                json.dump(hosting_config, config_file)
        except Exception as ex:
            # Best efforts removing invalid token is OK
            console.debug(
                f"Unable to delete the invalid token from config file, err: {ex}"
            )


def save_token_to_config(token: str, code: str | None = None):
    """Best efforts cache the token, and optionally invitation code to the config file.

    Args:
        token: The access token to save.
        code: The invitation code to save if exists.
    """
    hosting_config: dict[str, str] = {"access_token": token}
    if code:
        hosting_config["code"] = code
    try:
        if not os.path.exists(constants.Reflex.DIR):
            os.makedirs(constants.Reflex.DIR)
        with open(constants.Hosting.HOSTING_JSON, "w") as config_file:
            json.dump(hosting_config, config_file)
    except Exception as ex:
        console.warn(
            f"Unable to save token to {constants.Hosting.HOSTING_JSON} due to: {ex}"
        )


def requires_access_token() -> str:
    """Fetch the access token from the existing config if applicable.

    Returns:
        The access token. If not found, return empty string for it instead.
    """
    # Check if the user is authenticated

    access_token, _ = get_existing_access_token()
    if not access_token:
        console.debug("No access token found from the existing config.")

    return access_token


def authenticated_token() -> tuple[str, str]:
    """Fetch the access token from the existing config if applicable and validate it.

    Returns:
        The access token and the invitation code.
        If either is not found, return empty string for it instead.
    """
    # Check if the user is authenticated

    access_token, invitation_code = get_existing_access_token()
    if not access_token:
        console.debug("No access token found from the existing config.")
        access_token = ""
    elif not validate_token_with_retries(access_token):
        access_token = ""

    return access_token, invitation_code


def authorization_header(token: str) -> dict[str, str]:
    """Construct an authorization header with the specified token as bearer token.

    Args:
        token: The access token to use.

    Returns:
        The authorization header in dict format.
    """
    return {"Authorization": f"Bearer {token}"}


def requires_authenticated() -> str:
    """Check if the user is authenticated.

    Returns:
        The validated access token or empty string if not authenticated.
    """
    access_token, invitation_code = authenticated_token()
    if access_token:
        return access_token
    return authenticate_on_browser(invitation_code)


class DeploymentPrepInfo(BaseModel):
    """The params/settings returned from the prepare endpoint
    including the deployment key and the frontend/backend URLs once deployed.
    The key becomes part of both frontend and backend URLs.
    """

    # The deployment key
    key: str
    # The backend URL
    api_url: str
    # The frontend URL
    deploy_url: str


class DeploymentPrepareResponse(BaseModel):
    """The params/settings returned from the prepare endpoint,
    used in the CLI for the subsequent launch request.
    """

    # The app prefix, used on the server side only
    app_prefix: str
    # The reply from the server for a prepare request to deploy over a particular key
    # If reply is not None, it means server confirms the key is available for use.
    reply: Optional[DeploymentPrepInfo] = None
    # The list of existing deployments by the user under the same app name.
    # This is used to allow easy upgrade case when user attempts to deploy
    # in the same named app directory, user intends to upgrade the existing deployment.
    existing: Optional[List[DeploymentPrepInfo]] = None
    # The suggested key name based on the app name.
    # This is for a new deployment, user has not deployed this app before.
    # The server returns key suggestion based on the app name.
    suggestion: Optional[DeploymentPrepInfo] = None
    enabled_regions: Optional[List[str]] = None

    @root_validator(pre=True)
    def ensure_at_least_one_deploy_params(cls, values):
        """Ensure at least one set of param is returned for any of the cases we try to prepare.

        Args:
            values: The values passed in.

        Raises:
            ValueError: If all of the optional fields are None.

        Returns:
            The values passed in.
        """
        if (
            values.get("reply") is None
            and not values.get("existing")  # existing cannot be an empty list either
            and values.get("suggestion") is None
        ):
            raise ValueError(
                "At least one set of params for deploy is required from control plane."
            )
        return values


class DeploymentsPreparePostParam(BaseModel):
    """Params for app API URL creation backend API."""

    # The app name which is found in the config
    app_name: str
    # The deployment key
    key: Optional[str] = None  #  name of the deployment
    # The frontend hostname to deploy to. This is used to deploy at hostname not in the regular domain.
    frontend_hostname: Optional[str] = None


def prepare_deploy(
    app_name: str,
    key: str | None = None,
    frontend_hostname: str | None = None,
) -> DeploymentPrepareResponse:
    """Send a POST request to Control Plane to prepare a new deployment.
    Control Plane checks if there is conflict with the key if provided.
    If the key is absent, it will return existing deployments and a suggested name based on the app_name in the request.

    Args:
        key: The deployment name.
        app_name: The app name.
        frontend_hostname: The frontend hostname to deploy to. This is used to deploy at hostname not in the regular domain.

    Raises:
        Exception: If the operation fails. The exception message is the reason.

    Returns:
        The response containing the backend URLs if successful, None otherwise.
    """
    # Check if the user is authenticated
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")
    try:
        response = httpx.post(
            POST_DEPLOYMENTS_PREPARE_ENDPOINT,
            headers=authorization_header(token),
            json=DeploymentsPreparePostParam(
                app_name=app_name, key=key, frontend_hostname=frontend_hostname
            ).dict(exclude_none=True),
            timeout=HTTP_REQUEST_TIMEOUT,
        )

        response_json = response.json()
        console.debug(f"Response from prepare endpoint: {response_json}")
        if response.status_code == HTTPStatus.FORBIDDEN:
            console.debug(f'Server responded with 403: {response_json.get("detail")}')
            raise ValueError(f'{response_json.get("detail", "forbidden")}')
        response.raise_for_status()
        return DeploymentPrepareResponse(
            app_prefix=response_json["app_prefix"],
            reply=response_json["reply"],
            suggestion=response_json["suggestion"],
            existing=response_json["existing"],
            enabled_regions=response_json.get("enabled_regions"),
        )
    except httpx.RequestError as re:
        console.debug(f"Unable to prepare launch due to {re}.")
        raise Exception(str(re)) from re
    except httpx.HTTPError as he:
        console.debug(f"Unable to prepare deploy due to {he}.")
        raise Exception(f"{he}") from he
    except json.JSONDecodeError as jde:
        console.debug(f"Server did not respond with valid json: {jde}")
        raise Exception("internal errors") from jde
    except (KeyError, ValidationError) as kve:
        console.debug(f"The server response format is unexpected {kve}")
        raise Exception("internal errors") from kve
    except ValueError as ve:
        # This is a recognized client error, currently indicates forbidden
        raise Exception(f"{ve}") from ve
    except Exception as ex:
        console.debug(f"Unexpected error: {ex}.")
        raise Exception("internal errors") from ex


class DeploymentPostResponse(BaseModel):
    """The deploy POST request response. This could be backend or frontend."""

    # The URL
    url: str = Field(pattern=r"^https?://", min_length=8)
    # The sidecar URL, only relevant to backend
    sidecar_url: Optional[str] = Field(
        default=None, pattern=r"^https?://", min_length=8
    )
    # Deploy event ID
    event_id: int


class BackendDeploymentsPostParam(BaseModel):
    """Params for backend deployment POST request."""

    # Key is the name of the deployment, it becomes part of the URL
    key: Optional[str] = Field(default=None, pattern=r"^[a-z0-9-]+$")
    initiator_event_id: Optional[int] = None
    # Name of the app
    app_name: Optional[str] = Field(default=None, min_length=1)
    # json encoded list of regions to deploy to
    regions_json: Optional[str] = Field(default=None, min_length=1)
    # The app prefix, used on the server side only
    app_prefix: str = Field(..., min_length=1)
    # The version of reflex CLI used to deploy
    reflex_version: Optional[str] = Field(default=None, min_length=1)
    # The number of CPUs
    cpus: Optional[int] = None
    # The memory in MB
    memory_mb: Optional[int] = None
    # Whether to auto start the hosted deployment
    auto_start: Optional[bool] = None
    # Whether to auto stop the hosted deployment when idling
    auto_stop: Optional[bool] = None
    # The json encoded list of environment variables
    envs_json: Optional[str] = None
    # The command line prefix for tracing
    reflex_cli_entrypoint: Optional[str] = None
    # The metrics endpoint
    metrics_endpoint: Optional[str] = None
    # The reflex-hosting-cli version
    reflex_hosting_cli_version: Optional[str] = None
    # The user environment python version
    python_version: Optional[str] = None
    # The requirements.txt content as a single string
    requirements_txt: Optional[str] = None

    @root_validator(pre=True)
    def ensure_key_or_initiator_event_id(cls, values):
        """Ensure either key or initiator_event_id is provided.

        Args:
            values: The values passed in.

        Raises:
            ValueError: If neither key or initiator_event_id is provided.

        Returns:
            The values passed in.
        """
        if values.get("key") is None and values.get("initiator_event_id") is None:
            raise ValueError("Either key or initiator_event_id is required.")
        return values


class FrontendDeploymentsPostParam(BaseModel):
    """Params for frontend deployment POST request."""

    # Key is the name of the deployment, it becomes part of the URL
    key: Optional[str] = Field(default=None, pattern=r"^[a-z0-9-]+$")
    initiator_event_id: Optional[int] = None
    # The app prefix, used on the server side only
    app_prefix: str = Field(..., min_length=1)
    # The frontend hostname to deploy to. This is used to deploy at hostname not in the regular domain.
    frontend_hostname: Optional[str] = None

    @root_validator(pre=True)
    def ensure_key_or_initiator_event_id(cls, values):
        """Ensure either key or initiator_event_id is provided.

        Args:
            values: The values passed in.

        Raises:
            ValueError: If neither key or initiator_event_id is provided.

        Returns:
            The values passed in.
        """
        if values.get("key") is None and values.get("initiator_event_id") is None:
            raise ValueError("Either key or initiator_event_id is required.")
        return values


def deploy_backend(
    app_prefix: str,
    export_dir: str,
    backend_file_name: str,
    key: str | None = None,
    initiator_event_id: int | None = None,
    app_name: str | None = None,
    regions: list[str] | None = None,
    vm_type: str | None = None,
    cpus: int | None = None,
    memory_mb: int | None = None,
    auto_start: bool | None = None,
    auto_stop: bool | None = None,
    envs: dict[str, str] | None = None,
    with_tracing: str | None = None,
    with_metrics: str | None = None,
) -> DeploymentPostResponse:
    """Send a POST request to Control Plane to launch a backend deployment.

    Args:
        app_prefix: The app prefix.
        export_dir: The directory where the frontend/backend zip files are exported.
        backend_file_name: The backend file name.
        key: The deployment name.
        initiator_event_id: The initiator event ID.
        app_name: The app name.
        regions: The list of regions to deploy to.
        vm_type: The VM type.
        cpus: The number of CPUs.
        memory_mb: The memory in MB.
        auto_start: Whether to auto start.
        auto_stop: Whether to auto stop.
        envs: The environment variables.
        with_tracing: A string indicating the command line prefix for tracing.
        with_metrics: A string indicating the metrics endpoint.

    Raises:
        AssertionError: If the request is rejected by the hosting server.
        Exception: If the operation fails. The exception message is the reason.

    Returns:
        The response containing the backend URL of the site to be deployed and the deploy event ID if successful.
    """
    # Check if the user is authenticated
    if not (token := requires_access_token()):
        raise Exception("not authenticated")

    try:
        requirements_txt = None
        if (encoding := detect_encoding(constants.RequirementsTxt.FILE)) is not None:
            with open(constants.RequirementsTxt.FILE, "r", encoding=encoding) as f:
                requirements_txt = f.read()

        params = BackendDeploymentsPostParam(
            key=key,
            initiator_event_id=initiator_event_id,
            app_name=app_name,
            regions_json=json.dumps(regions) if regions else None,
            app_prefix=app_prefix,
            cpus=cpus,
            memory_mb=memory_mb,
            auto_start=auto_start,
            auto_stop=auto_stop,
            envs_json=json.dumps(envs) if envs else None,
            reflex_version=metadata.version(constants.Reflex.MODULE_NAME),
            reflex_cli_entrypoint=with_tracing,
            metrics_endpoint=with_metrics,
            python_version=platform.python_version(),
            reflex_hosting_cli_version=metadata.version(
                constants.ReflexHostingCli.MODULE_NAME
            ),
            requirements_txt=requirements_txt,
        )

        with open(os.path.join(export_dir, backend_file_name), "rb") as backend_file:
            # https://docs.python-requests.org/en/latest/user/advanced/#post-multiple-multipart-encoded-files
            files = [
                ("files", (backend_file_name, backend_file)),
            ]
            response = httpx.post(
                POST_DEPLOYMENTS_ENDPOINT,
                headers=authorization_header(token),
                data=params.dict(exclude_none=True),
                files=files,
                timeout=HTTP_REQUEST_TIMEOUT,
            )
        # If the server explicitly states bad request,
        # display a different error
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise AssertionError(f"Server rejected this request: {response.text}")
        response.raise_for_status()
        response_json = response.json()
        return DeploymentPostResponse(
            url=response_json["backend_url"],
            event_id=response_json["backend_event_id"],
            sidecar_url=response_json["backend_sidecar_url"],
        )
    except (FileNotFoundError, OSError) as oe:
        console.error(f"Client side error related to file operation: {oe}")
        raise
    except httpx.RequestError as re:
        console.error(f"Unable to deploy due to request error: {re}")
        raise Exception("request error") from re
    except httpx.HTTPError as he:
        console.error(f"Unable to deploy due to {he}.")
        raise Exception(str) from he
    except json.JSONDecodeError as jde:
        console.error(f"Server did not respond with valid json: {jde}")
        raise Exception("internal errors") from jde
    except (KeyError, ValidationError) as kve:
        console.error(f"Post params or server response format unexpected: {kve}")
        raise Exception("internal errors") from kve
    except AssertionError as ve:
        console.error(f"Unable to deploy due to request error: {ve}")
        # re-raise the error back to the user as client side error
        raise
    except Exception as ex:
        console.error(f"Unable to deploy due to internal errors: {ex}.")
        raise Exception("internal errors") from ex


def deploy_frontend(
    app_prefix: str,
    export_dir: str,
    frontend_file_name: str,
    key: str | None = None,
    initiator_event_id: int | None = None,
    frontend_hostname: str | None = None,
) -> DeploymentPostResponse:
    """Send a POST request to Control Plane to launch a frontend deployment.

    Args:
        app_prefix: The app prefix.
        export_dir: The directory where the frontend/backend zip files are exported.
        frontend_file_name: The frontend file name.
        key: The deployment name.
        initiator_event_id: The initiator event ID.
        frontend_hostname: The frontend hostname to deploy to. This is used to deploy at hostname not in the regular domain.

    Raises:
        AssertionError: If the request is rejected by the hosting server.
        Exception: If the operation fails. The exception message is the reason.

    Returns:
        The response containing the frontend URL of the site to be deployed and the deploy event ID if successful.
    """
    # Check if the user is authenticated
    if not (token := requires_access_token()):
        raise Exception("not authenticated")

    try:
        params = FrontendDeploymentsPostParam(
            app_prefix=app_prefix,
            key=key,
            initiator_event_id=initiator_event_id,
            frontend_hostname=frontend_hostname,
        )

        with open(os.path.join(export_dir, frontend_file_name), "rb") as frontend_file:
            # https://docs.python-requests.org/en/latest/user/advanced/#post-multiple-multipart-encoded-files
            files = [
                ("files", (frontend_file_name, frontend_file)),
            ]
            response = httpx.post(
                POST_DEPLOYMENTS_ENDPOINT,
                headers=authorization_header(token),
                data=params.dict(exclude_none=True),
                files=files,
                timeout=HTTP_REQUEST_TIMEOUT,
            )
        # If the server explicitly states bad request,
        # display a different error
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise AssertionError(f"Server rejected this request: {response.text}")
        response.raise_for_status()
        response_json = response.json()
        return DeploymentPostResponse(
            url=response_json["frontend_url"],
            event_id=response_json["frontend_event_id"],
        )
    except OSError as oe:
        console.error(f"Client side error related to file operation: {oe}")
        raise
    except httpx.RequestError as re:
        console.error(f"Unable to deploy due to request error: {re}")
        raise Exception("request error") from re
    except httpx.HTTPError as he:
        console.error(f"Unable to deploy due to {he}.")
        raise Exception(str) from he
    except json.JSONDecodeError as jde:
        console.error(f"Server did not respond with valid json: {jde}")
        raise Exception("internal errors") from jde
    except (KeyError, ValidationError) as kve:
        console.error(f"Post params or server response format unexpected: {kve}")
        raise Exception("internal errors") from kve
    except AssertionError as ve:
        console.error(f"Unable to deploy due to request error: {ve}")
        # re-raise the error back to the user as client side error
        raise
    except Exception as ex:
        console.error(f"Unable to deploy due to internal errors: {ex}.")
        raise Exception("internal errors") from ex


class DeploymentsGetParam(BaseModel):
    """Params for hosted instance GET request."""

    # The app name which is found in the config
    app_name: Optional[str]


def list_deployments(
    app_name: str | None = None,
) -> list[dict]:
    """Send a GET request to Control Plane to list deployments.

    Args:
        app_name: the app name as an optional filter when listing deployments.

    Raises:
        Exception: If the operation fails. The exception message shows the reason.

    Returns:
        The list of deployments if successful, None otherwise.
    """
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")

    params = DeploymentsGetParam(app_name=app_name)

    try:
        response = httpx.get(
            GET_DEPLOYMENTS_ENDPOINT,
            headers=authorization_header(token),
            params=params.dict(exclude_none=True),
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as re:
        console.error(f"Unable to list deployments due to request error: {re}")
        raise Exception("request timeout") from re
    except httpx.HTTPError as he:
        console.error(f"Unable to list deployments due to {he}.")
        raise Exception("internal errors") from he
    except (ValidationError, KeyError, json.JSONDecodeError) as vkje:
        console.error(f"Server response format unexpected: {vkje}")
        raise Exception("internal errors") from vkje
    except Exception as ex:
        console.error(f"Unexpected error: {ex}.")
        raise Exception("internal errors") from ex


def fetch_token(request_id: str) -> tuple[str, str]:
    """Fetch the access token for the request_id from Control Plane.

    Args:
        request_id: The request ID used when the user opens the browser for authentication.

    Returns:
        The access token if it exists, None otherwise.
    """
    access_token = invitation_code = ""
    try:
        resp = httpx.get(
            f"{FETCH_TOKEN_ENDPOINT}/{request_id}",
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        access_token = (resp_json := resp.json()).get("access_token", "")
        invitation_code = resp_json.get("code", "")
    except httpx.RequestError as re:
        console.debug(f"Unable to fetch token due to request error: {re}")
    except httpx.HTTPError as he:
        console.debug(f"Unable to fetch token due to {he}")
    except json.JSONDecodeError as jde:
        console.debug(f"Server did not respond with valid json: {jde}")
    except KeyError as ke:
        console.debug(f"Server response format unexpected: {ke}")
    except Exception:
        console.debug("Unexpected errors: {ex}")

    return access_token, invitation_code


def poll_backend_sidecar_with_retries(sidecar_url: str) -> bool:
    """Poll the backend sidecar with retries.

    Args:
        sidecar_url: The URL of the backend sidecar.

    Returns:
        Boolean indicating whether the backend sidecar is reachable.
    """
    for _ in range(constants.Hosting.BACKEND_SIDECAR_WAIT_AND_PING_DURATION):
        console.debug(f"Polling backend sidecar at {sidecar_url}")
        try:
            ping_response = httpx.get(f"{sidecar_url}", timeout=1)
            ping_response.raise_for_status()
            return True

        except httpx.HTTPError as hpe:
            console.debug(f"Backend sidecar responded with: {hpe}")
            time.sleep(1)
    console.debug(
        f"After {constants.Hosting.BACKEND_SIDECAR_WAIT_AND_PING_DURATION} retries, backend sidecar is still not reachable. Likely the deployment was not successful."
    )
    return False


def check_stacktrace_in_log_lines(
    log_json: list[dict], current_from_iso_timestamp: datetime
) -> tuple[int, datetime]:
    """Check if there is a stacktrace in the log lines.

    Args:
        log_json: The log lines.
        current_from_iso_timestamp: The `from` timestamp used to fetch log_json.

    Returns:
        A tuple of integer and optional timestamp:
            The index of the log line where the stacktrace starts if found, -1 otherwise;
            And the `from` timestamp for the next log query.
    """
    next_from_iso_timestamp = current_from_iso_timestamp
    # The return is expected to be a list of dicts
    for idx, row in enumerate(log_json):
        if (message := row.get("message")) is None:
            continue
        message = message.lower()
        if APP_LOG_STACKTRACE_WORD in message:
            # we detect error and eagerly return to user
            return idx, next_from_iso_timestamp

        if (
            maybe_timestamp := convert_to_local_time_with_tz(row["timestamp"])
        ) is not None:
            console.debug(
                f"Updating from {next_from_iso_timestamp} to {maybe_timestamp}"
            )
            # Add a small delta so does not poll the same logs
            next_from_iso_timestamp = maybe_timestamp + timedelta(microseconds=1e5)
        else:
            console.warn(f"Unable to parse timestamp {row['timestamp']}")

    return -1, next_from_iso_timestamp


def poll_backend_ping_endpoint_check_app_stacktrace_with_retries(
    key: str, backend_ping_url: str, from_iso_timestamp: datetime
) -> tuple[bool, str | None]:
    """Poll the backend ping endpoint and check app logs for stacktrace with retries.

    Args:
        key: The name of the deployment.
        backend_ping_url: The URL of the backend ping endpoint.
        from_iso_timestamp: The `from` (oldest) timestamp to fetch the logs from.

    Raises:
        Exception: If not authenticated.

    Returns:
        A tuple of boolean and optional string: indicating whether the backend is reachable and optionally the detailed error message if backend is not responsive.
    """
    # For log query, we need to be authenticated
    if not (token := requires_access_token()):
        raise Exception("not authenticated")

    stacktrace_start_index_in_logs = -1
    ping_success = False
    for _ in range(constants.Hosting.BACKEND_REFLEX_APP_PING_LOG_QUERY_RETRIES):
        # If already pinged through, no need to ping again
        if not ping_success:
            console.debug(f"Polling backend ping endpoint at {backend_ping_url}")
            try:
                ping_response = httpx.get(f"{backend_ping_url}", timeout=1)
                ping_response.raise_for_status()
                ping_success = True
            except httpx.HTTPError as hpe:
                console.debug(f"Ping endpoint responded with {hpe}")
        try:
            log_response = httpx.post(
                POST_DEPLOYMENT_LOGS_ENDPOINT,
                json={
                    "key": key,
                    "log_type": LogType.APP_LOG.value,
                    "from_iso_timestamp": from_iso_timestamp.astimezone().isoformat(),
                },
                headers=authorization_header(token),
                timeout=LOG_QUERY_TIMEOUT,
            )
            log_response.raise_for_status()
            log_json = log_response.json()
            console.debug(f"log server responded with {log_json}")

            (
                stacktrace_start_index_in_logs,
                from_iso_timestamp,
            ) = check_stacktrace_in_log_lines(
                log_json=log_json, current_from_iso_timestamp=from_iso_timestamp
            )
            if stacktrace_start_index_in_logs >= 0:
                # Format the tail bounded by a limit as multi-line string
                # For each line, format is: "timestamp | message"
                stacktrace_tail = [
                    " | ".join(
                        [
                            convert_to_local_time_str(row["timestamp"]),
                            row["message"],
                        ]
                    )
                    for row in log_json[
                        stacktrace_start_index_in_logs : stacktrace_start_index_in_logs
                        + APP_LOG_STACKTRACE_LINE_LIMIT
                    ]
                ]
                return False, "\n".join(stacktrace_tail)
        except httpx.HTTPError as hpe:
            console.debug(f"Log endpoint responded with: {hpe}")
        except (json.JSONDecodeError, KeyError, TypeError):
            console.debug("Unable to parse the returned logs")
        time.sleep(1)

    return ping_success, None


def poll_backend_with_retries(
    key: str,
    from_iso_timestamp: datetime,
    backend_url: str,
    sidecar_url: str,
) -> tuple[bool, str | None]:
    """Poll the backend with retries. Backend of the reflex is deployed
    behind a proxy with sidecar. The sidecar is designed to come up
    and respond immediately to indicate the deployment is successful.
    The backend of reflex app can take additional time. Based on this,
    first poll the sidecar, then poll the backend while fetching the logs.
    Early return these logs as part of the error message.

    Args:
        key: the name of the deployment
        from_iso_timestamp: the timestamp to fetch the logs from
        backend_url: the URL of the backend of the deployed app
        sidecar_url: the URL of the sidecar of the deployed app

    Returns:
        A tuple of boolean and optional string: indicating whether the backend is reachable and optionally the detailed error message if backend is not responsive.
    """
    # This backend poll happens after the milestone events indicate success
    # If any errors, we expect those most probably are coming the user app
    backend_ping_url = f"{backend_url}/ping"

    with console.status("Checking backend ..."):
        if not poll_backend_sidecar_with_retries(sidecar_url=sidecar_url):
            return False, None

        return poll_backend_ping_endpoint_check_app_stacktrace_with_retries(
            key=key,
            backend_ping_url=backend_ping_url,
            from_iso_timestamp=from_iso_timestamp,
        )


def poll_frontend_with_retries(frontend_url: str) -> bool:
    """Poll the frontend with retries to check if it is up.

    Args:
        frontend_url: The URL of the frontend to poll.

    Returns:
        Boolean indicating whether the frontend is reachable.
    """
    with console.status("Checking frontend ..."):
        for _ in range(constants.Hosting.FRONTEND_POLL_DURATION):
            try:
                console.debug(f"Polling frontend at {frontend_url}")
                resp = httpx.get(f"{frontend_url}", timeout=1)
                resp.raise_for_status()
                return True
            except httpx.HTTPError:
                time.sleep(1)

    return False


class DeploymentDeleteParam(BaseModel):
    """Params for hosted instance DELETE request."""

    # key is the name of the deployment, it becomes part of the site URL
    key: str


def delete_deployment(key: str):
    """Send a DELETE request to Control Plane to delete a deployment.

    Args:
        key: The deployment name.

    Raises:
        ValueError: If the key is not provided.
        Exception: If the operation fails. The exception message is the reason.
    """
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")
    if not key:
        raise ValueError("Valid key is required for the delete.")

    try:
        response = httpx.delete(
            f"{DELETE_DEPLOYMENTS_ENDPOINT}/{key}",
            headers=authorization_header(token),
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        response.raise_for_status()

    except httpx.TimeoutException as te:
        console.error("Unable to delete deployment due to request timeout.")
        raise Exception("request timeout") from te
    except httpx.HTTPError as he:
        console.error(f"Unable to delete deployment due to {he}.")
        raise Exception("internal errors") from he
    except Exception as ex:
        console.error(f"Unexpected errors {ex}.")
        raise Exception("internal errors") from ex


class SiteStatus(BaseModel):
    """Deployment status info."""

    # The frontend URL
    frontend_url: Optional[str] = None
    # The backend URL
    backend_url: Optional[str] = None
    # Whether the frontend/backend URL is reachable
    reachable: bool
    # The last updated iso formatted timestamp if site is reachable
    updated_at: Optional[str] = None

    @root_validator(pre=True)
    def ensure_one_of_urls(cls, values):
        """Ensure at least one of the frontend/backend URLs is provided.

        Args:
            values: The values passed in.

        Raises:
            ValueError: If none of the URLs is provided.

        Returns:
            The values passed in.
        """
        if values.get("frontend_url") is None and values.get("backend_url") is None:
            raise ValueError("At least one of the URLs is required.")
        return values


class DeploymentStatusResponse(BaseModel):
    """Response for deployment status request."""

    # The frontend status
    frontend: SiteStatus
    # The backend status
    backend: SiteStatus


def get_deployment_status(key: str) -> DeploymentStatusResponse:
    """Get the deployment status.

    Args:
        key: The deployment name.

    Raises:
        ValueError: If the key is not provided.
        Exception: If the operation fails. The exception message is the reason.

    Returns:
        The deployment status response including backend and frontend.
    """
    if not key:
        raise ValueError(
            "A non empty key is required for querying the deployment status."
        )

    if not (token := requires_authenticated()):
        raise Exception("not authenticated")

    try:
        response = httpx.get(
            f"{GET_DEPLOYMENT_STATUS_ENDPOINT}/{key}/status",
            headers=authorization_header(token),
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        response_json = response.json()
        return DeploymentStatusResponse(
            frontend=SiteStatus(
                frontend_url=response_json["frontend"]["url"],
                reachable=response_json["frontend"]["reachable"],
                updated_at=response_json["frontend"]["updated_at"],
            ),
            backend=SiteStatus(
                backend_url=response_json["backend"]["url"],
                reachable=response_json["backend"]["reachable"],
                updated_at=response_json["backend"]["updated_at"],
            ),
        )
    except Exception as ex:
        console.error(f"Unable to get deployment status due to {ex}.")
        raise Exception("internal errors") from ex


def convert_to_local_time_with_tz(iso_timestamp: str) -> datetime | None:
    """Helper function to convert the iso timestamp to local time.

    Args:
        iso_timestamp: The iso timestamp to convert.

    Returns:
        The converted timestamp with timezone.
    """
    try:
        return dateutil.parser.isoparse(iso_timestamp).astimezone()
    except (TypeError, ValueError) as ex:
        # In certain scenarios such as the app status cannot be
        # fetched, it is expected the server returns None,
        # the conversion will fail but should not print error here.
        console.debug(f"Unable to convert iso timestamp {iso_timestamp} due to {ex}.")
        return None


def convert_to_local_time_str(iso_timestamp: str) -> str:
    """Convert the iso timestamp to local time.

    Args:
        iso_timestamp: The iso timestamp to convert.

    Returns:
        The converted timestamp string.
    """
    if (local_dt := convert_to_local_time_with_tz(iso_timestamp)) is None:
        return iso_timestamp
    return local_dt.strftime("%Y-%m-%d %H:%M:%S.%f %Z")


class LogType(str, enum.Enum):
    """Enum for log types."""

    # Logs printed from the user code, the "app"
    APP_LOG = "app"
    # Build logs are the server messages while building/running user deployment
    BUILD_LOG = "build"
    # Deploy logs are specifically for the messages at deploy time
    # returned to the user the current stage of the deployment, such as building, uploading.
    DEPLOY_LOG = "deploy"
    # All the logs which can be printed by all above types.
    ALL_LOG = "all"


async def stream_logs(
    key: str,
    log_type: LogType = LogType.APP_LOG,
    from_iso_timestamp: str | None = None,
):
    """Get the deployment logs and stream on console.

    Args:
        key: The deployment name.
        log_type: The type of logs to query from server.
                  See the LogType definitions for how they are used.
        from_iso_timestamp: An optional timestamp with timezone info to limit
                            where the log queries should start from.

    Raises:
        ValueError: If the key is not provided.
        Exception: If the operation fails. The exception message is the reason.

    """
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")
    if not key:
        raise ValueError("Valid key is required for querying logs.")
    try:
        logs_endpoint = f"{DEPLOYMENT_LOGS_ENDPOINT}/{key}/logs?access_token={token}&log_type={log_type.value}"
        console.debug(f"log server endpoint: {logs_endpoint}")
        if from_iso_timestamp is not None:
            logs_endpoint += f"&from_iso_timestamp={from_iso_timestamp}"
        _ws = websockets.connect(logs_endpoint)  # type: ignore
        async with _ws as ws:
            while True:
                row_json = json.loads(await ws.recv())
                console.debug(f"Server responded with logs: {row_json}")
                if row_json and isinstance(row_json, dict):
                    row_to_print = {}
                    for k, v in row_json.items():
                        if v is None:
                            row_to_print[k] = str(v)
                        elif k == "timestamp":
                            row_to_print[k] = convert_to_local_time_str(v)
                        else:
                            row_to_print[k] = v
                    print(" | ".join(row_to_print.values()))
                else:
                    console.debug("Server responded, no new logs, this is normal")
    except Exception as ex:
        console.debug(f"Unable to get more deployment logs due to {ex}.")
        console.print("Log server disconnected ...")
        console.print(
            "Note that the server has limit to only stream logs for several minutes"
        )


def get_logs(
    key: str,
    log_type: LogType = LogType.APP_LOG,
    from_iso_timestamp: str | None = None,
    to_iso_timestamp: str | None = None,
    limit: int | None = None,
):
    """Get the deployment logs and print on console. This is roughly equivalent to `stream_logs` but return logs in one shot.

    Args:
        key: The deployment name.
        log_type: The type of logs to query from server.
                  See the LogType definitions for how they are used.
        from_iso_timestamp: An optional timestamp with timezone info to limit
                            where the log queries should start from.
        to_iso_timestamp: An optional timestamp with timezone info to limit
                          where the log queries should end at.
        limit: An optional limit to the number of logs to query.

    Raises:
        ValueError: If the key is not provided.
        Exception: If the operation fails. The exception message is the reason.

    """
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")
    if not key:
        raise ValueError("Valid key is required for querying logs.")
    try:
        params_json = {
            "key": key,
            "log_type": log_type.value,
            "from_iso_timestamp": from_iso_timestamp,
            "to_iso_timestamp": to_iso_timestamp,
            "lookback_limit": limit,
        }
        console.debug(f"log server params: {params_json}")
        log_response = httpx.post(
            POST_DEPLOYMENT_LOGS_ENDPOINT,
            json=params_json,
            headers=authorization_header(token),
            timeout=LOG_QUERY_TIMEOUT,
        )
        log_response.raise_for_status()
        log_json = log_response.json()
        console.debug(f"log server responded with {log_json}")
        for row_json in log_json:
            row_to_print = {}
            for k, v in row_json.items():
                if v is None:
                    row_to_print[k] = str(v)
                elif k == "timestamp":
                    row_to_print[k] = convert_to_local_time_str(v)
                else:
                    row_to_print[k] = v
            print(" | ".join(row_to_print.values()))

    except httpx.HTTPError as he:
        console.debug(f"Unable to get more deployment logs due to {he}.")
    except (AttributeError, TypeError, ValueError) as ex:
        console.error(f"Unable to process the server response: {ex}.")


def check_requirements_txt_exist() -> bool:
    """Check if requirements.txt exists in the top level app directory.

    Returns:
        True if requirements.txt exists, False otherwise.
    """
    return os.path.exists(constants.RequirementsTxt.FILE)


def check_requirements_for_non_reflex_packages() -> bool:
    """Check the requirements.txt file for packages other than reflex.

    Returns:
        True if packages other than reflex are found, False otherwise.
    """
    if not check_requirements_txt_exist():
        return False
    try:
        with open(constants.RequirementsTxt.FILE) as fp:
            for req_line in fp.readlines():
                package_name = re.search(r"^([^=<>!~]+)", req_line.lstrip())
                # If we find a package that is not reflex
                if (
                    package_name
                    and package_name.group(1) != constants.Reflex.MODULE_NAME
                ):
                    return True
    except Exception as ex:
        console.warn(f"Unable to scan requirements.txt for dependencies due to {ex}")

    return False


def authenticate_on_browser(invitation_code: str) -> str:
    """Open the browser to authenticate the user.

    Args:
        invitation_code: The invitation code if it exists.

    Returns:
        The access token if valid, empty otherwise.
    """
    console.print(f"Opening {constants.Hosting.CP_WEB_URL} ...")
    request_id = uuid.uuid4().hex
    auth_url = (
        f"{constants.Hosting.CP_WEB_URL}?request-id={request_id}&code={invitation_code}"
    )
    if not webbrowser.open(auth_url):
        console.warn(
            f"Unable to automatically open the browser. Please go to {auth_url} to authenticate."
        )
    access_token = invitation_code = ""
    with console.status("Waiting for access token ..."):
        for _ in range(constants.Hosting.WEB_AUTH_RETRIES):
            access_token, invitation_code = fetch_token(request_id)
            if access_token:
                break
            else:
                time.sleep(constants.Hosting.WEB_AUTH_SLEEP_DURATION)

    if access_token and validate_token_with_retries(access_token):
        save_token_to_config(access_token, invitation_code)
    else:
        access_token = ""
    return access_token


def validate_token_with_retries(access_token: str) -> bool:
    """Validate the access token with retries.

    Args:
        access_token: The access token to validate.

    Returns:
        True if the token is valid,
        False if invalid or unable to validate.
    """
    with console.status("Validating access token ..."):
        for _ in range(constants.Hosting.WEB_AUTH_RETRIES):
            try:
                validate_token(access_token)
                return True
            except ValueError:
                console.error(f"Access denied")
                delete_token_from_config()
                break
            except Exception as ex:
                console.debug(f"Unable to validate token due to: {ex}, trying again")
                time.sleep(constants.Hosting.WEB_AUTH_SLEEP_DURATION)
    return False


def is_valid_deployment_key(key: str):
    """Helper function to check if the deployment key is valid. Must be a domain name safe string.

    Args:
        key: The deployment key to check.

    Returns:
        True if the key contains only domain name safe characters, False otherwise.
    """
    return re.match(r"^[a-zA-Z0-9-]*$", key)


def interactive_get_deployment_key_from_user_input(
    pre_deploy_response: DeploymentPrepareResponse,
    app_name: str,
    frontend_hostname: str | None = None,
) -> tuple[str, str, str]:
    """Interactive get the deployment key from user input.

    Args:
        pre_deploy_response: The response from the initial prepare call to server.
        app_name: The app name.
        frontend_hostname: The frontend hostname to deploy to. This is used to deploy at hostname not in the regular domain.

    Returns:
        The deployment key, backend URL, frontend URL.
    """
    key_candidate = api_url = deploy_url = ""
    if reply := pre_deploy_response.reply:
        api_url = reply.api_url
        deploy_url = reply.deploy_url
        key_candidate = reply.key
    elif pre_deploy_response.existing:
        # validator already checks existing field is not empty list
        # Note: keeping this simple as we only allow one deployment per app
        existing = pre_deploy_response.existing[0]
        console.print(f"Overwrite deployment [ {existing.key} ] ...")
        key_candidate = existing.key
        api_url = existing.api_url
        deploy_url = existing.deploy_url
    elif suggestion := pre_deploy_response.suggestion:
        key_candidate = suggestion.key
        api_url = suggestion.api_url
        deploy_url = suggestion.deploy_url

        # If user takes the suggestion, we will use the suggested key and proceed
        while key_input := console.ask(
            f"Choose a name for your deployed app (https://<picked-name>.reflex.run)\nEnter to use default.",
            default=key_candidate,
        ):
            if not is_valid_deployment_key(key_input):
                console.error(
                    "Invalid key input, should only contain domain name safe characters: letters, digits, or hyphens."
                )
                continue

            elif any(x.isupper() for x in key_input):
                key_input = key_input.lower()
                console.info(
                    f"Domain name is case insensitive, automatically converting to all lower cases: {key_input}"
                )

            try:
                pre_deploy_response = prepare_deploy(
                    app_name,
                    key=key_input,
                    frontend_hostname=frontend_hostname,
                )
                if (
                    pre_deploy_response.reply is None
                    or key_input != pre_deploy_response.reply.key
                ):
                    # Rejected by server, try again
                    continue
                key_candidate = pre_deploy_response.reply.key
                api_url = pre_deploy_response.reply.api_url
                deploy_url = pre_deploy_response.reply.deploy_url
                # we get the confirmation, so break from the loop
                break
            except Exception:
                console.error(
                    "Cannot deploy at this name, try picking a different name"
                )

    return key_candidate, api_url, deploy_url


def process_envs(envs: list[str]) -> dict[str, str]:
    """Process the environment variables.

    Args:
        envs: The environment variables expected in key=value format.

    Raises:
        SystemExit: If the envs are not in valid format.

    Returns:
        The processed environment variables in a dict.
    """
    processed_envs = {}
    for env in envs:
        kv = env.split("=", maxsplit=1)
        if len(kv) != 2:
            raise SystemExit("Invalid env format: should be <key>=<value>.")

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", kv[0]):
            raise SystemExit(
                "Invalid env name: should start with a letter or underscore, followed by letters, digits, or underscores."
            )
        processed_envs[kv[0]] = kv[1]
    return processed_envs


def log_out_on_browser():
    """Open the browser to authenticate the user."""
    # Fetching existing invitation code so user sees the log out page without having to enter it
    invitation_code = None
    with contextlib.suppress(Exception):
        _, invitation_code = get_existing_access_token()
        console.debug("Found existing invitation code in config")
        delete_token_from_config()
    console.print(f"Opening {constants.Hosting.CP_WEB_URL} ...")
    if not webbrowser.open(f"{constants.Hosting.CP_WEB_URL}?code={invitation_code}"):
        console.warn(
            f"Unable to open the browser automatically. Please go to {constants.Hosting.CP_WEB_URL} to log out."
        )


def poll_deploy_milestones(
    key: str, from_iso_timestamp: datetime, deploy_event_ids: list[int]
) -> bool | None:
    """Periodically poll the hosting server for deploy milestones.

    Args:
        key: The deployment key.
        from_iso_timestamp: The timestamp of the deployment request time, this helps with the milestone query.
        deploy_event_ids: The list of deploy event IDs to query.

    Raises:
        ValueError: If a non-empty key is not provided.
        Exception: If the user is not authenticated.

    Returns:
        False if server reports back failure, True otherwise. None if do not receive the end of deployment message.
    """
    if not key:
        raise ValueError("Non-empty key is required for querying deploy status.")
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")

    expected_success_messages_count = len(END_OF_DEPLOYMENT_MESSAGES)
    success_messages = set()
    for _ in range(DEPLOYMENT_EVENT_MESSAGES_RETRIES):
        try:
            response = httpx.post(
                POST_DEPLOYMENT_LOGS_ENDPOINT,
                json={
                    "key": key,
                    "log_type": LogType.DEPLOY_LOG.value,
                    "from_iso_timestamp": from_iso_timestamp.astimezone().isoformat(),
                    "deploy_event_ids": deploy_event_ids,
                },
                headers=authorization_header(token),
            )
            response.raise_for_status()
            response_json = response.json()
            # The return is expected to be a list of dicts
            for row in response_json:
                console.print(
                    " | ".join(
                        [
                            local_time_str := convert_to_local_time_str(
                                row["timestamp"]
                            ),
                            row["message"],
                        ]
                    )
                )
                # If any details returned in the milestone,
                # print them here without the timestamp,
                # with the intention to make it look like a sub level message
                if message_details := row.get("details"):
                    for det in message_details.splitlines():
                        console.print(
                            " | ".join(
                                [
                                    # we print the same number of spaces as the timestamp instead
                                    # depending on the font, this might not create a consistently
                                    # aligned indentation on user terminal
                                    " " * len(local_time_str),
                                    det,
                                ]
                            )
                        )
                # Update the `from`` timestamp to the last timestamp of received message
                if (
                    maybe_timestamp := convert_to_local_time_with_tz(row["timestamp"])
                ) is not None:
                    console.debug(
                        f"Updating from {from_iso_timestamp} to {maybe_timestamp}"
                    )
                    # Add a small delta so does not poll the same logs
                    from_iso_timestamp = maybe_timestamp + timedelta(microseconds=1e5)
                else:
                    console.warn(f"Unable to parse timestamp {row['timestamp']}")
                server_message = row["message"].lower()
                if "fail" in server_message:
                    console.debug(
                        "Received failure message, stop event message streaming"
                    )
                    return False
                if any(msg in server_message for msg in END_OF_DEPLOYMENT_MESSAGES):
                    success_messages.add(server_message)
                    if len(success_messages) == expected_success_messages_count:
                        console.debug(
                            "Received end of deployment message, stop event message streaming"
                        )
                        return True
            time.sleep(1)
        except httpx.HTTPError as he:
            # This includes HTTP server and client error
            console.debug(f"Unable to get more deployment events due to {he}.")
        except Exception as ex:
            console.warn(f"Unable to parse server response due to {ex}.")


async def display_deploy_milestones(key: str, from_iso_timestamp: datetime) -> bool:
    """Display the deploy milestone messages reported back from the hosting server.

    Args:
        key: The deployment key.
        from_iso_timestamp: The timestamp of the deployment request time, this helps with the milestone query.

    Raises:
        ValueError: If a non-empty key is not provided.
        Exception: If the user is not authenticated.

    Returns:
        False if server reports back failure, True otherwise.
    """
    if not key:
        raise ValueError("Non-empty key is required for querying deploy status.")
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")

    try:
        logs_endpoint = f"{DEPLOYMENT_LOGS_ENDPOINT}/{key}/logs?access_token={token}&log_type={LogType.DEPLOY_LOG.value}&from_iso_timestamp={from_iso_timestamp.astimezone().isoformat()}"
        console.debug(f"log server endpoint: {logs_endpoint}")
        _ws = websockets.connect(logs_endpoint)  # type: ignore
        expected_success_messages_count = len(END_OF_DEPLOYMENT_MESSAGES)
        success_messages = set()
        async with _ws as ws:
            # Stream back the deploy events reported back from the server
            for _ in range(DEPLOYMENT_EVENT_MESSAGES_RETRIES):
                row_json = json.loads(await ws.recv())
                console.debug(f"Server responded with: {row_json}")
                if row_json and isinstance(row_json, dict):
                    # Only show the timestamp and actual message
                    console.print(
                        " | ".join(
                            [
                                convert_to_local_time_str(row_json["timestamp"]),
                                row_json["message"],
                            ]
                        )
                    )
                    server_message = row_json["message"].lower()
                    if "fail" in server_message:
                        console.debug(
                            "Received failure message, stop event message streaming"
                        )
                        return False
                    if any(msg in server_message for msg in END_OF_DEPLOYMENT_MESSAGES):
                        success_messages.add(server_message)
                        if len(success_messages) == expected_success_messages_count:
                            console.debug(
                                "Received end of deployment message, stop event message streaming"
                            )
                            return True
                else:
                    console.debug("Server responded, no new events yet, this is normal")
    except Exception as ex:
        console.debug(f"Unable to get more deployment events due to {ex}.")
    return False


def wait_for_server_to_pick_up_request():
    """Wait for server to pick up the request. Right now is just sleep."""
    with console.status(
        f"Waiting for server to pick up request ~ {DEPLOYMENT_PICKUP_DELAY} seconds ..."
    ):
        for _ in range(DEPLOYMENT_PICKUP_DELAY):
            time.sleep(1)


def interactive_prompt_for_envs() -> list[str]:
    """Interactive prompt for environment variables.

    Returns:
        The list of environment variables in key=value string format.
    """
    envs = []
    envs_finished = False
    env_count = 1
    env_key_prompt = f" * env-{env_count} name (enter to skip)"
    console.print("Environment variables for your production App ...")
    while not envs_finished:
        env_key = console.ask(env_key_prompt)
        if not env_key:
            envs_finished = True
            if envs:
                console.print("Finished adding envs.")
            else:
                console.print("No envs added. Continuing ...")
            break
        # If it possible to have empty values for env, so we do not check here
        env_value = console.ask(f"   env-{env_count} value")
        envs.append(f"{env_key}={env_value}")
        env_count += 1
        env_key_prompt = f" * env-{env_count} name (enter to skip)"
    return envs


def get_regions() -> list[dict]:
    """Get the supported regions from the hosting server.

    Returns:
        A list of dict representation of the region information.
    """
    try:
        response = httpx.get(
            GET_REGIONS_ENDPOINT,
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        response_json = response.json()
        if response_json is None or not isinstance(response_json, list):
            console.error("Expect server to return a list ")
            return []
        if (
            response_json
            and response_json[0] is not None
            and not isinstance(response_json[0], dict)
        ):
            console.error("Expect return values are dict's")
            return []
        return response_json
    except Exception as ex:
        console.error(f"Unable to get regions due to {ex}.")
        return []


def prompt_for_regions(
    enabled_regions: list[str] | None = None,
    regions_args: list[str] | None = None,
) -> list[str]:
    """Prompt for user to enter the regions to deploy to.

    Args:
        enabled_regions: The list of enabled regions.
        regions_args: The regions passed in as command line arguments.

    Returns:
        The list of regions to deploy to as entered by the user.
    """
    regions = regions_args or []
    # Then CP needs to know the user's location, which requires user permission
    while True:
        region_input = console.ask(
            "Region to deploy to. See regions: https://bit.ly/46Qr3mF\nEnter to use default.",
            default=regions[0] if regions else "sjc",
        )

        if enabled_regions is None or region_input in enabled_regions:
            break
        else:
            console.warn(
                f"{region_input} is not a valid region. Must be one of {enabled_regions}"
            )
            console.warn("Run `reflex deployments regions` to see details.")
    return regions or [region_input]


UNIT_TO_KWARGS = {
    "d": "days",
    "h": "hours",
    "m": "minutes",
    "s": "seconds",
}


def process_user_entered_timestamp(
    timestamp: str, reference: datetime = datetime.now().astimezone()
) -> str | None:
    """Process the user entered timestamp.

    Args:
        timestamp: The timestamp string entered by the user.
        reference: The reference timestamp to calculate the returned timestamp from.

    Returns:
        The processed timestamp string in ISO 8601 format. If unable to process, return None.
    """
    if not timestamp:
        return None

    # Check if the timestamp is in the format of <number><unit>, such as 1d, 2h, 3m, 4s
    match = re.match(r"^(\d+)([dhms])$", timestamp)
    if match:
        number, character = match.groups()
        kwargs = {UNIT_TO_KWARGS[character]: int(number)}
        return (reference - timedelta(**kwargs)).isoformat()

    # Check if the timestamp is already a valid ISO 8601 timestamp
    try:
        return dateutil.parser.isoparse(timestamp).isoformat()
    except ValueError:
        console.debug(f"Unable to parse the timestamp {timestamp} as ISO format")

    # Check if the timestamp is a unix epoch timestamp
    try:
        return datetime.fromtimestamp(float(timestamp)).astimezone().isoformat()
    except ValueError:
        console.debug(f"The timestamp is not a valid unix epoch timestamp: {timestamp}")
    except (OSError, OverflowError) as ex:
        console.warn(
            f"Unable to convert the timestamp ({timestamp}) as unix epoch timestamp: {ex}"
        )
    return None


def _validate_url_with_protocol_prefix(url: str | None) -> bool:
    """Validate the URL with protocol prefix. Empty string is acceptable.

    Args:
        url: the URL string to check.

    Returns:
        Whether the entered URL is acceptable.
    """
    return not url or (url.startswith("http://") or url.startswith("https://"))


def _process_entered_list(input: str | None) -> list | None:
    """Process the user entered comma separated list into a list if applicable.

    Args:
        input: the user entered comma separated list

    Returns:
        The list of items or None.
    """
    return [t.strip() for t in (input or "").split(",") if t if input] or None


def _get_file_from_prompt_in_loop() -> tuple[bytes, str] | None:
    image_file = file_extension = None
    while image_file is None:
        image_filepath = console.ask(
            f"Upload a preview image of your demo app (enter to skip)"
        )
        if not image_filepath:
            break
        file_extension = image_filepath.split(".")[-1]
        try:
            with open(image_filepath, "rb") as f:
                image_file = f.read()
                return image_file, file_extension
        except OSError as ose:
            console.error(f"Unable to read the {file_extension} file due to {ose}")
            raise typer.Exit(code=1) from ose

    console.debug(f"File extension detected: {file_extension}")
    return None


def collect_deployment_info_interactive(
    key: str | None = None, demo_url: str | None = None
):
    """Collect the deployment information interactively from the user.

    Args:
        key: The deployment key.
        demo_url: The demo URL.

    Raises:
        Exception: If the user is not authenticated.
        Exit: Requests to backend services failed.
    """
    if not (token := requires_authenticated()):
        raise Exception("not authenticated")

    params = {}

    # Either key or demo_url is required.
    if not key and not demo_url:
        while True:
            demo_url = (
                console.ask(
                    "[ Full URL of deployed app, e.g. `https://my-app.reflex.run` ]"
                )
                or None
            )
            if _validate_url_with_protocol_prefix(demo_url):
                break

    if key:
        params["key"] = key
    if demo_url:
        params["demo_url"] = demo_url

    try:
        # Verify the user has permission by sending POST request
        # in case the subsequent steps of collecting information are interrupted.
        console.debug(f"Sending POST to verify user permission: {params}")
        response = httpx.post(
            POST_GALLERY_APPS_ENDPOINT,
            data=params,
            headers=authorization_header(token),
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        if response.status_code == httpx.codes.FORBIDDEN:
            console.error(
                f"You do not have permission to update the gallery data for {demo_url}."
            )
            raise typer.Exit(code=1)
        response.raise_for_status()
    except httpx.HTTPError as he:
        console.error(f"Unable to verify user permission due to {he}.")
        raise typer.Exit(code=1) from he

    files = []
    if (image_file_and_extension := _get_file_from_prompt_in_loop()) is not None:
        files.append(
            ("files", (image_file_and_extension[1], image_file_and_extension[0]))
        )

    if display_name := (
        console.ask("[ Friendly display name for your app ] (enter to skip)") or None
    ):
        params["display_name"] = display_name

    if keywords := _process_entered_list(
        console.ask("[ Keywords separated by commas ] (enter to skip)")
    ):
        params["keywords"] = keywords

    if (
        summary := console.ask("[ Short description of your app ] (enter to skip)")
        or None
    ):
        params["summary"] = summary

    source = None
    while True:
        source = (
            console.ask(
                "[ Full URL of source code, e.g. `https://github.com/owner/repo` ]"
            )
            or None
        )
        if _validate_url_with_protocol_prefix(source):
            params["source"] = source
            break

    # Now send the post request to Reflex backend services.
    try:
        console.debug(f"Sending gallery app data: {params}")
        response = httpx.post(
            POST_GALLERY_APPS_ENDPOINT,
            data=params,
            files=files,
            headers=authorization_header(token),
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        response.raise_for_status()

    except httpx.HTTPError as he:
        console.error(f"Unable to complete request due to {he}.")
        raise typer.Exit(code=1) from he

    console.info("Gallery app information successfully shared!")
