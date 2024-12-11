"""Hosting service related utilities."""

from __future__ import annotations

import contextlib
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import time
import uuid
import webbrowser
from http import HTTPStatus
from typing import Any, Dict, List

import httpx
import typer

import reflex_cli.constants as constants
from reflex_cli.utils import console, dependency
from reflex_cli.utils.dependency import is_valid_url
from reflex_cli.utils.exceptions import NotAuthenticatedError


class SilentBackgroundBrowser(webbrowser.BackgroundBrowser):
    """A webbrowser.BackgroundBrowser that does not raise exceptions when it fails to open a browser."""

    def open(self, url):
        """Open url in a new browser window.

        Args:
            url (str): The URL to open.

        Returns:
            bool: True if the URL was opened successfully, False otherwise.

        """
        cmdline = [self.name] + [arg.replace("%s", url) for arg in self.args]
        sys.audit("webbrowser.open", url)
        try:
            if sys.platform[:3] == "win":
                p = subprocess.Popen(
                    cmdline, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            else:
                p = subprocess.Popen(
                    cmdline,
                    close_fds=True,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return p.poll() is None
        except OSError:
            return False


webbrowser.BackgroundBrowser = SilentBackgroundBrowser


def get_existing_access_token() -> str:
    """Fetch the access token from the existing config if applicable.

    Returns:
        The access token.
        If not found, return empty string for it instead.
    """
    console.debug("Fetching token from existing config...")
    access_token = ""
    try:
        with open(constants.Hosting.HOSTING_JSON, "r") as config_file:
            hosting_config = json.load(config_file)
            access_token = hosting_config.get("access_token", "")
    except Exception as ex:
        console.debug(
            f"Unable to fetch token from {constants.Hosting.HOSTING_JSON} due to: {ex}"
        )
    return access_token


def validate_token(token: str) -> dict[str, Any]:
    """Validate the token with the control plane.

    Args:
        token: The access token to validate.

    Returns:
        Information about the user associated with the token.

    Raises:
        ValueError: if access denied.
        Exception: if runs into timeout, failed requests, unexpected errors. These should be tried again.

    """
    try:
        response = httpx.post(
            f"{constants.Hosting.HOSTING_SERVICE}/v1/authenticate/me",
            headers=authorization_header(token),
            timeout=constants.Hosting.TIMEOUT,
        )
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise ValueError
        response.raise_for_status()
        return response.json()
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
        include_invitation_code: Used by the previous hosting service (ignored)

    """
    if os.path.exists(constants.Hosting.HOSTING_JSON):
        try:
            with open(constants.Hosting.HOSTING_JSON, "w") as config_file:
                hosting_config = json.load(config_file)
                del hosting_config["access_token"]
                json.dump(hosting_config, config_file)
        except Exception as ex:
            # Best efforts removing invalid token is OK
            console.debug(
                f"Unable to delete the invalid token from config file, err: {ex}"
            )
    # Delete the previous hosting service data if present.
    if os.path.exists(constants.Hosting.HOSTING_JSON_V0):
        os.remove(constants.Hosting.HOSTING_JSON_V0)


def save_token_to_config(token: str):
    """Best efforts cache the token to the config file.

    Args:
        token: The access token to save.
    """
    hosting_config: dict[str, str] = {"access_token": token}

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

    access_token = get_existing_access_token()
    if not access_token:
        console.debug("No access token found from the existing config.")

    return access_token


def authenticated_token() -> tuple[str, dict[str, Any]]:
    """Fetch the access token from the existing config if applicable and validate it.

    Returns:
        The access token and validated user info.
        If not found, return empty string and dict for it instead.
    """
    # Check if the user is authenticated

    validated_info = {}
    access_token = get_existing_access_token()
    if access_token and not (
        validated_info := validate_token_with_retries(access_token)
    ):
        access_token = ""

    return access_token, validated_info


def authorization_header(token: str) -> dict[str, str]:
    """Construct an authorization header with the specified token as bearer token.

    Args:
        token: The access token to use.

    Returns:
        The authorization header in dict format.

    """
    try:
        uuid.UUID(token, version=4)
    except ValueError:
        return {"Authorization": f"Bearer {token}"}
    else:
        return {"X-API-TOKEN": token}


def requires_authenticated() -> str:
    """Check if the user is authenticated.

    Returns:
        The validated access token or empty string if not authenticated.

    """
    access_token, _ = authenticated_token()
    if access_token:
        return access_token
    access_token, _ = authenticate_on_browser()
    return access_token


def search_app(app_name: str, project_id: str | None, token: str | None = None) -> dict:
    """Search for an application by name within a specific project.

    Args:
        app_name (str): The name of the application to search for.
        project_id (str | None): The ID of the project to search within. If None, searches across all projects.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        dict: The search results as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.
        Exception: If the search request fails.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    if project_id is None:
        project_id = ""
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE
        + f"/v1/apps/search?app_name={app_name}&project_id={project_id}",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        raise Exception(f"deployment failed: {ex_details}") from ex
    response_json = response.json()
    return response_json


def get_app(app_id: str, token: str | None = None) -> dict:
    """Retrieve details of a specific application by its ID.

    Args:
        app_id (str): The ID of the application to retrieve.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        dict: The application details as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/{app_id}",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def create_app(
    app_name: str, description: str, project_id: str | None, token: str | None = None
):
    """Create a new application.

    Args:
        app_name (str): The name of the application.
        description (str): The description of the application.
        project_id (str | None): The ID of the project to associate the application with.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        dict: The created application details as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.
        ValueError: If forbidden.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/",
        json={"name": app_name, "description": description, "project": project_id},
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response_json = response.json()
    if response.status_code == HTTPStatus.FORBIDDEN:
        console.debug(f'Server responded with 403: {response_json.get("detail")}')
        raise ValueError(f'{response_json.get("detail", "forbidden")}')
    response.raise_for_status()
    return response_json


def get_hostname(
    app_id: str, app_name: str, hostname: str | None, token: str | None = None
) -> dict:
    """Retrieve or reserve a hostname for a specific application.

    Args:
        app_id (str): The ID of the application.
        app_name (str): The name of the application.
        hostname (str | None): The desired hostname. If None, a hostname will be generated.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        dict: The hostname details as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.
        Exception: If deployment fails or the hostname is invalid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")

    data = {"app_id": app_id, "app_name": app_name}
    if hostname:
        clean_hostname = extract_subdomain(hostname)
        if clean_hostname is None:
            raise Exception("bad hostname provided")
        data["hostname"] = clean_hostname
    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/reserve",
        headers=authorization_header(token),
        json=data,
        timeout=constants.Hosting.TIMEOUT,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        if ex_details == "hostname taken":
            return {"error": "hostname taken"}
        raise Exception(f"deployment failed: {ex_details}") from ex
    response_json = response.json()
    return response_json


def extract_subdomain(url):
    """Extract the subdomain from a given URL.

    Args:
        url (str): The URL to extract the subdomain from.

    Returns:
        str | None: The extracted subdomain, or None if extraction fails.

    """
    from urllib.parse import urlparse

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed_url = urlparse(url)
    netloc = parsed_url.netloc

    if netloc.startswith("www."):
        netloc = netloc[4:]

    parts = netloc.split(".")

    if len(parts) >= 2 or len(parts) == 1:
        return parts[0]

    return None


def get_secrets(app_id: str, token: str | None = None) -> str:
    """Retrieve secrets for a given application.

    Args:
        app_id (str): The ID of the application.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The secrets as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/{app_id}/secrets",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        try:
            return ex.response.json().get("detail")
        except json.JSONDecodeError:
            return ex.response.text
    return response.json()


def update_secrets(
    app_id: str, secrets: dict, reboot: bool = False, token: str | None = None
):
    """Update secrets for a given application.

    Args:
        app_id (str): The ID of the application.
        secrets (dict): The secrets to update.
        reboot (bool): Whether to reboot the application with the new secrets.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The updated secrets as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE
        + f"/v1/apps/{app_id}/secrets?reboot={'true' if reboot else 'false'}",
        headers=authorization_header(token),
        json={"secrets": secrets},
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def delete_secret(
    app_id: str, key: str, reboot: bool = False, token: str | None = None
) -> str:
    """Delete a secret for a given application.

    Args:
        app_id (str): The ID of the application.
        key (str): The key of the secret to delete.
        reboot (bool): Whether to reboot the application with the updated secrets.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The response from the delete operation as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.delete(
        constants.Hosting.HOSTING_SERVICE
        + f"/v1/apps/{app_id}/secrets/{key}?reboot={'true' if reboot else 'false'}",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        try:
            return ex.response.json().get("detail")
        except json.JSONDecodeError:
            return ex.response.text
    return response.json()


def create_project(name: str, token: str | None = None):
    """Create a new project.

    Args:
        name (str): The name of the project.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        dict: The created project details as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.
        ValueError: If the request to create the project fails.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/create",
        json={"name": name},
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response_json = response.json()
    if response.status_code == HTTPStatus.BAD_REQUEST:
        console.debug(f'Server responded with 400: {response_json.get("detail")}')
        raise ValueError(f'{response_json.get("detail", "bad request")}')
    response.raise_for_status()
    return response_json


def select_project(project: str, token: str | None = None) -> str:
    """Select a project by its ID.

    Args:
        project (str): The ID of the project to select.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        None

    """
    try:
        with open(constants.Hosting.HOSTING_JSON, "r") as config_file:
            hosting_config = json.load(config_file)
        with open(constants.Hosting.HOSTING_JSON, "w") as config_file:
            hosting_config["project"] = project
            json.dump(hosting_config, config_file)
    except Exception as ex:
        return (
            f"failed to fetch token from {constants.Hosting.HOSTING_JSON} due to: {ex}"
        )
    return f"{project} is now selected."


def get_selected_project() -> str | None:
    """Retrieve the currently selected project ID.

    Returns:
        str | None: The ID of the selected project, or None if no project is selected.

    """
    try:
        with open(constants.Hosting.HOSTING_JSON, "r") as config_file:
            hosting_config = json.load(config_file)
            return hosting_config.get("project")
    except Exception as ex:
        console.debug(
            f"Unable to fetch token from {constants.Hosting.HOSTING_JSON} due to: {ex}"
        )
    return None


def get_projects(token: str | None = None) -> list[dict]:
    """Retrieve a list of projects.

    Args:
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The list of projects as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project(project_id: str, token: str | None = None):
    """Retrieve a single project given the project ID.

    Args:
        project_id (str): The ID of the project.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The project details as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/{project_id}",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_usage(project_id: str, token: str | None = None):
    """Retrieve the usage statistics for a project.

    Args:
        project_id (str): The ID of the project.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The usage statistics as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/{project_id}/usage",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_roles(project_id: str, token: str | None = None):
    """Retrieve the roles for a project.

    Args:
        project_id (str): The ID of the project.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The roles as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/{project_id}/roles",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_role_permissions(
    project_id: str, role_id: str, token: str | None = None
):
    """Retrieve the permissions for a specific role in a project.

    Args:
        project_id (str): The ID of the project.
        role_id (str): The ID of the role.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The role permissions as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/{project_id}/role/{role_id}",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_role_users(project_id: str, token: str | None = None):
    """Retrieve the users for a project.

    Args:
        project_id (str): The ID of the project.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The users as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/{project_id}/users",
        headers=authorization_header(token),
        timeout=constants.Hosting.TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def invite_user_to_project(role_id: str, user_id: str, token: str | None = None) -> str:
    """Invite a user to a project with a specific role.

    Args:
        role_id (str): The ID of the role to assign to the user.
        user_id (str): The ID of the user to invite.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The response from the invite operation as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE + f"/v1/project/users/invite",
        headers=authorization_header(token),
        json={"user_id": user_id, "role_id": role_id},
        timeout=constants.Hosting.TIMEOUT,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        try:
            return ex.response.json().get("detail")
        except json.JSONDecodeError:
            return ex.response.text
    return response.json()


def validate_deployment_args(
    app_name: str,
    project_id: str | None,
    regions: List[str] | None,
    vmtype: str | None,
    hostname: str | None,
    token: str | None,
) -> str:
    """Validate the deployment arguments.

    Args:
        app_name: The name of the application.
        project_id: The ID of the project to associate the deployment with.
        regions: The list of regions for the deployment.
        vmtype: The VM type for the deployment.
        hostname: The hostname for the deployment.
        token: The authentication token. If None, attempts to authenticate.

    Returns:
        The validation result as a string -- "success" if all checks pass.
    """
    if not token and not (token := requires_authenticated()):
        return "not authenticated"

    param_data = {
        "app_name": app_name or "",
        "project_id": project_id or "",
        "regions": json.dumps(regions or []),
        "vmtype": vmtype or "",
        "hostname": hostname or "",
    }
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + "/v1/deployments/validate_cli",
        headers=authorization_header(token),
        params=param_data,
        timeout=15,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        try:
            ex_details = ex.response.json().get("detail")
            return f"deployment failed: {ex_details}"
        except (httpx.RequestError, ValueError, KeyError):
            return "deployment failed: internal server error"

    return "success"


def create_deployment(
    app_name: str,
    project_id: str | None,
    regions: list | None,
    zip_dir: str,
    hostname: str | None,
    vmtype: str | None,
    secrets: dict | None,
    token: str | None = None,
) -> str:
    """Create a new deployment for an application.

    Args:
        app_name (str): The name of the application.
        project_id (str | None): The ID of the project to associate the deployment with.
        regions (list | None): The list of regions for the deployment.
        zip_dir (str): The directory containing the zip files for the deployment.
        hostname (str | None): The hostname for the deployment.
        vmtype (str | None): The VM type for the deployment.
        secrets (dict | None): The secrets to use for the deployment.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The deployment id.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    cli_version = importlib.metadata.version("reflex-hosting-cli")
    zips = [
        (
            "files",
            (
                "backend.zip",
                open(os.path.join(zip_dir, "backend.zip"), "rb"),  # noqa: SIM115
            ),
        ),
        (
            "files",
            (
                "frontend.zip",
                open(os.path.join(zip_dir, "frontend.zip"), "rb"),  # noqa: SIM115
            ),
        ),
    ]
    payload: Dict[str, Any] = {
        "app_name": app_name,
        "reflex_hosting_cli_version": cli_version,
        "reflex_version": dependency.get_reflex_version(),
        "python_version": platform.python_version(),
    }
    if project_id:
        payload["project_id"] = project_id
    if regions:
        regions = regions if regions else []
        payload["regions"] = json.dumps(regions)
    if hostname:
        payload["hostname"] = hostname
    if vmtype:
        payload["vm_type"] = vmtype
    if secrets:
        payload["secrets"] = json.dumps(secrets)

    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE + f"/v1/deployments",
        data=payload,
        files=zips,
        headers=authorization_header(token),
        timeout=55,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        try:
            ex_details = ex.response.json().get("detail")
            return f"deployment failed: {ex_details}"
        except (httpx.RequestError, ValueError, KeyError):
            return "deployment failed: internal server error"
    return response.json()


def stop_app(app_id: str, token: str | None = None):
    """Stop a running application.

    Args:
        app_id (str): The ID of the application.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The response from the stop operation as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/{app_id}/stop",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"stop app failed: {ex_details}"
    return response.json()


def start_app(app_id: str, token: str | None = None):
    """Start a stopped application.

    Args:
        app_id (str): The ID of the application.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The response from the start operation as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.post(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/{app_id}/start",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"start app failed: {ex_details}"
    return response.json()


def delete_app(app_id: str, token: str | None = None):
    """Delete an application.

    Args:
        app_id (str): The ID of the application.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The response from the delete operation as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    app = get_app(app_id=app_id)
    if not app:
        console.warn("no app with given id found")
        return
    response = httpx.delete(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/{app['id']}/delete",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"delete app failed: {ex_details}"
    return response.json()


def get_app_logs(
    app_id: str,
    offset: int | None,
    start: int | None,
    end: int | None,
    token: str | None,
):
    """Retrieve logs for a given application.

    Args:
        app_id (str): The ID of the application.
        offset (int | None): The offset in seconds from the current time.
        start (int | None): The start time in Unix epoch format.
        end (int | None): The end time in Unix epoch format.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        The logs as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    app = get_app(app_id=app_id)
    if not app:
        console.warn("no app with given id found")
        return
    params = f"?offset={offset}" if offset else f"?start={start}&end={end}"
    try:
        response = httpx.get(
            constants.Hosting.HOSTING_SERVICE + f"/v1/apps/{app['id']}/logs{params}",
            headers=authorization_header(token),
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"get app logs failed: {ex_details}"
    return response.json()


def list_apps(project: str | None = None, token: str | None = None) -> List[dict]:
    """List all the hosted deployments of the authenticated user.

    Args:
        project (str | None): The project ID to filter deployments.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        List[dict]: A list of deployments as dictionaries.

    Raises:
        NotAuthenticatedError: If the token is not valid.
        Exception: when listing apps fails.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    if project:
        url = constants.Hosting.HOSTING_SERVICE + f"/v1/apps?project={project}"
    else:
        url = constants.Hosting.HOSTING_SERVICE + f"/v1/apps"

    response = httpx.get(url, headers=authorization_header(token), timeout=5)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        raise Exception(f"list app failed: {ex_details}") from ex
    return response.json()


def get_app_history(app_id: str, token: str | None = None) -> list:
    """Retrieve the deployment history for a given application.

    Args:
        app_id (str): The ID of the application.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        list: A list of deployment history entries as dictionaries.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/apps/{app_id}/history",
        headers=authorization_header(token),
    )

    response.raise_for_status()
    result = []
    response_json = response.json()
    for deployment in response_json:
        result.append(
            {
                "id": deployment["id"],
                "status": deployment["status"],
                "hostname": deployment["hostname"],
                "python version": deployment["python_version"],
                "reflex version": deployment["reflex_version"],
                "vm type": deployment["vm_type"],
                "timestamp": deployment["timestamp"],
            }
        )
    return result


def get_app_status(app_id: str, token: str | None) -> str:
    """Retrieve the status of a specific app.

    Args:
        app_id (str): The ID of the app.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        str: The status of the app.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    try:
        response = httpx.get(
            constants.Hosting.HOSTING_SERVICE + f"/v1/deployments/{app_id}/status",
            headers=authorization_header(token),
        )
    except httpx.RequestError:
        return "lost connection: trying again"

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        return "error: bad response. received a bad response from cloud service."
    return response.json()


def get_deployment_status(deployment_id: str, token: str | None = None) -> str:
    """Retrieve the status of a specific deployment.

    Args:
        deployment_id (str): The ID of the deployment.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        str: The status of the deployment.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE + f"/v1/deployments/{deployment_id}/status",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"get status failed: {ex_details}"
    return response.json()


def _get_deployment_status(deployment_id: str, token: str) -> str:
    """Retrieve the status of a specific deployment with error handling.

    Args:
        deployment_id (str): The ID of the deployment.
        token (str): The authentication token.

    Returns:
        str: The status of the deployment, or an error message if the request fails.

    """
    try:
        response = httpx.get(
            constants.Hosting.HOSTING_SERVICE
            + f"/v1/deployments/{deployment_id}/status",
            headers=authorization_header(token),
        )
    except httpx.RequestError:
        return "lost connection: trying again"

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        return "error: bad response. received a bad response from cloud service."
    return response.json()


def watch_deployment_status(deployment_id: str, token: str | None = None) -> bool:
    """Continuously watch the status of a specific deployment.

    Args:
        deployment_id (str): The ID of the deployment.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        False when the watching ends.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    with console.status("listening to status updates!"):
        current_status = ""
        while True:
            status = _get_deployment_status(deployment_id=deployment_id, token=token)
            if "completed successfully" in status:
                console.success(status)
                break
            if "build error" in status:
                console.warn(status)
                console.warn(
                    f"to see the build logs:\n reflex cloud apps build-logs {deployment_id}"
                )
                break
            if "unable to find status for given id" in status:
                console.error(status)
                break
            if "error" in status:
                console.warn(status)
                break
            if status == current_status:
                continue
            current_status = status
            console.info(status)
            time.sleep(0.5)
    return False


def get_deployment_build_logs(deployment_id: str, token: str | None = None):
    """Retrieve the build logs for a specific deployment.

    Args:
        deployment_id (str): The ID of the deployment.
        token (str | None): The authentication token. If None, attempts to authenticate.

    Returns:
        dict: The build logs as a dictionary.

    Raises:
        NotAuthenticatedError: If the token is not valid.

    """
    if not token and not (token := requires_authenticated()):
        raise NotAuthenticatedError("not authenticated")
    response = httpx.get(
        constants.Hosting.HOSTING_SERVICE
        + f"/v1/deployments/{deployment_id}/build/logs",
        headers=authorization_header(token),
    )

    response.raise_for_status()
    return response.json()


def list_projects():
    """List all projects.

    This function is currently a placeholder and does not perform any operations.

    Returns:
        None

    """
    return None


def fetch_token(request_id: str) -> str:
    """Fetch the access token for the request_id from Control Plane.

    Args:
        request_id (str): The request ID used when the user opens the browser for authentication.

    Returns:
        The access token if it exists, empty strings otherwise.
    """
    access_token = ""
    try:
        resp = httpx.get(
            f"{constants.Hosting.HOSTING_SERVICE}/v1/authenticate/{request_id}",
            timeout=constants.Hosting.TIMEOUT,
        )
        resp.raise_for_status()
        access_token = (resp_json := resp.json()).get("access_token", "")
        project_id = resp_json.get("user_id", "")
        select_project(project=project_id)
    except httpx.RequestError as re:
        console.debug(f"Unable to fetch token due to request error: {re}")
    except httpx.HTTPError as he:
        console.debug(f"Unable to fetch token due to {he}")
    except json.JSONDecodeError as jde:
        console.debug(f"Server did not respond with valid json: {jde}")
    except KeyError as ke:
        console.debug(f"Server response format unexpected: {ke}")
    except Exception as ex:
        console.debug(f"Unexpected errors: {ex}")

    return access_token


def authenticate_on_browser(invitation_code=None) -> tuple[str, dict[str, Any]]:
    """Open the browser to authenticate the user.

    Args:
        invitation_code (str): Used by the previous hosting service (ignored)

    Returns:
        The access token if valid and user information dict otherwise ("", {}).

    Raises:
        Exit: when the hosting service URL is invalid.

    """
    console.print(f"Opening {constants.Hosting.HOSTING_SERVICE_UI} ...")

    if not is_valid_url(constants.Hosting.HOSTING_SERVICE_UI):
        console.error(
            f"Invalid hosting URL: {constants.Hosting.HOSTING_SERVICE_UI}. Ensure the URL is in the correct format and includes a valid scheme"
        )
        raise typer.Exit(1)
    request_id = uuid.uuid4().hex
    auth_url = f"{constants.Hosting.HOSTING_SERVICE_UI}?request-id={request_id}"
    if not webbrowser.open(auth_url):
        console.warn(
            f"Unable to automatically open the browser. Please go to {auth_url} to authenticate."
        )
    validated_info = {}
    access_token = ""
    console.ask("please hit 'Enter' or 'Return' after login on website complete")
    with console.status("Waiting for access token ..."):
        for _ in range(constants.Hosting.AUTH_RETRY_LIMIT):
            access_token = fetch_token(request_id)
            if access_token:
                break
            else:
                time.sleep(1)

    if access_token and (validated_info := validate_token_with_retries(access_token)):
        save_token_to_config(access_token)
    else:
        access_token = ""
    return access_token, validated_info


def validate_token_with_retries(access_token: str) -> dict[str, Any]:
    """Validate the access token with retries.

    Args:
        access_token (str): The access token to validate.

    Returns:
        validated user info dict.

    """
    with console.status("Validating access token ..."):
        for _ in range(constants.Hosting.AUTH_RETRY_LIMIT):
            try:
                return validate_token(access_token)
            except ValueError:
                console.error(f"Access denied")
                delete_token_from_config()
                break
            except Exception as ex:
                console.debug(f"Unable to validate token due to: {ex}, trying again")
                time.sleep(constants.Hosting.AUTH_RETRY_SLEEP_DURATION)
    return {}


def process_envs(envs: list[str]) -> dict[str, str]:
    """Process the environment variables.

    Args:
        envs (list[str]): The environment variables expected in key=value format.

    Raises:
        SystemExit: If the envs are not in valid format.

    Returns:
        dict[str, str]: The processed environment variables in a dictionary.

    Raises:
        SystemExit: If invalid format.

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
    """Open the browser to log out the user."""
    with contextlib.suppress(Exception):
        delete_token_from_config()
    console.print(f"Opening {constants.Hosting.HOSTING_SERVICE_UI} ...")
    if not webbrowser.open(constants.Hosting.HOSTING_SERVICE_UI):
        console.warn(
            f"Unable to open the browser automatically. Please go to {constants.Hosting.HOSTING_SERVICE_UI} to log out."
        )


def get_vm_types() -> list[dict]:
    """Retrieve the available VM types.

    Returns:
        list[dict]: A list of VM types as dictionaries.

    """
    try:
        response = httpx.get(
            constants.Hosting.HOSTING_SERVICE + "/v1/deployments/vm_types",
            timeout=10,
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
        console.error(f"Unable to get vmtypes due to {ex}.")
        return []


def get_regions() -> list[dict]:
    """Get the supported regions from the hosting server.

    Returns:
        list[dict]: A list of dict representation of the region information.

    """
    try:
        response = httpx.get(
            constants.Hosting.HOSTING_SERVICE + "/v1/deployments/regions",
            timeout=10,
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
        result = []
        for region in response_json:
            result.append({"name": region["name"], "code": region["code"]})
        return result
    except Exception as ex:
        console.error(f"Unable to get regions due to {ex}.")
        return []
