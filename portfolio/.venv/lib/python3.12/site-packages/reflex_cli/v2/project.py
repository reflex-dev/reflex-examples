"""Project commands for the Reflex Cloud CLI."""

import json
from typing import Optional

import typer
from tabulate import tabulate
from typing_extensions import Annotated

from reflex_cli import constants
from reflex_cli.utils import console
from reflex_cli.utils.exceptions import NotAuthenticatedError

project_cli = typer.Typer()


@project_cli.command(name="create")
def create_project(
    name: str = typer.Argument(..., help="The name of the project."),
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """Create a new project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    project = hosting.create_project(name=name, token=token)
    if as_json:
        console.print(json.dumps(project))
        return
    if project:
        project = [project]
        headers = list(project[0].keys())
        table = [list(p.values()) for p in project]
        console.print(tabulate(table, headers=headers))
    else:
        console.print(str(project))


@project_cli.command(name="invite")
def invite_user_to_project(
    role: str = typer.Argument(..., help="The role ID to assign to the user."),
    user: str = typer.Argument(..., help="The user ID to invite."),
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
):
    """Invite a user to a project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    try:
        result = hosting.invite_user_to_project(role_id=role, user_id=user, token=token)
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise typer.Exit(1) from err

    if "failed" in result:
        console.error(f"Unable to invite user to project: {result}")
        raise typer.Exit(1)
    console.success("Successfully invited user to project.")


@project_cli.command(name="select")
def select_project(
    project: str = typer.Argument(..., help="The project ID to select."),
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
):
    """Select a project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    result = hosting.select_project(project=project, token=token)
    if "failed" in result:
        console.error(result)
        raise typer.Exit(1)
    console.success(result)


@project_cli.command(name="selected")
def get_select_project(
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    token: Optional[str] = typer.Option(None, help="The authentication token."),
):
    """Get the currently selected project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    project = hosting.get_selected_project()
    if project:
        try:
            project_details = hosting.get_project(project_id=project, token=token)
            console.print(
                tabulate(
                    [[project, project_details["name"]]],
                    headers=["Selected Project ID", "Project Name"],
                )
            )
        except NotAuthenticatedError:
            console.error(
                "You are not authenticated. Run `reflex login` to authenticate."
            )
            typer.Exit(1)
        except Exception as e:
            console.error(f"Unable to get the currently selected project: {e}")
    else:
        console.warn(
            "no selected project. run `reflex cloud project select` to set one."
        )


@project_cli.command(name="list")
def get_projects(
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """Retrieve a list of projects."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    try:
        projects = hosting.get_projects(token=token)
        if as_json:
            console.print(json.dumps(projects))
            return
        if projects:
            headers = list(projects[0].keys())
            table = [list(project.values()) for project in projects]
            console.print(tabulate(table, headers=headers))
        else:
            # If returned empty list, print the empty
            console.print(str(projects))
    except NotAuthenticatedError:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        typer.Exit(1)
    except Exception as e:
        console.error(f"Unable to get projects: {e}")
        raise typer.Exit(1) from e


@project_cli.command(name="usage")
def get_project_usage(
    project_id: Optional[str] = typer.Option(
        None,
        help="The ID of the project. If not provided, the selected project will be used. If no project is selected, it throws an error.",
    ),
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in JSON format."
    ),
):
    """Retrieve the usage statistics for a project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    try:
        if project_id is None:
            project_id = hosting.get_selected_project()
        if project_id is None:
            console.error(
                "no project_id provided or selected. Set it with `reflex cloud project usage --project-id \\[project_id]`"
            )
            raise typer.Exit(1)

        usage = hosting.get_project_usage(project_id=project_id, token=token)

        if as_json:
            console.print(json.dumps(usage))
            return
        if usage:
            headers = ["Deployments", "CPU (cores)", "Memory (gb)"]
            table = [
                [
                    f'{usage["deployment_count"]}/{usage["tier"]["deployment_quota"]}',
                    f'{usage["cpu_usage"]}/{usage["tier"]["cpu_quota"]}',
                    f'{usage["memory_usage"]}/{usage["tier"]["ram_quota"]}',
                ]
            ]
            console.print(tabulate(table, headers=headers))
        else:
            # If returned empty list, print the empty
            console.print(str(usage))
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise typer.Exit(1) from err


@project_cli.command(name="roles")
def get_project_roles(
    project_id: Optional[str] = typer.Option(
        None,
        help="The ID of the project. If not provided, the selected project will be used. If no project_id is provided or selected throws an error.",
    ),
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """Retrieve the roles for a project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    try:
        if project_id is None:
            project_id = hosting.get_selected_project()
        if project_id is None:
            console.error(
                "no project_id provided or selected. Set it with `reflex cloud project roles --project-id \\[project_id]`"
            )
            raise typer.Exit(1)

        roles = hosting.get_project_roles(project_id=project_id, token=token)

        if as_json:
            console.print(json.dumps(roles))
            return
        if roles:
            headers = list(roles[0].keys())
            table = [list(role.values()) for role in roles]
            console.print(tabulate(table, headers=headers))
        else:
            # If returned empty list, print the empty
            console.print(str(roles))
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise typer.Exit(1) from err


@project_cli.command(name="role-permissions")
def get_project_role_permissions(
    role_id: str = typer.Argument(..., help="The ID of the role."),
    project_id: Optional[str] = typer.Option(
        None,
        help="The ID of the project. If not provided, the selected project will be used. If no project is selected, it throws an error.",
    ),
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """Retrieve the permissions for a specific role in a project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)
    try:
        if project_id is None:
            project_id = hosting.get_selected_project()
        if project_id is None:
            console.error(
                "no project_id provided or selected. Set it with `reflex cloud project role-permissions --project-id \\[project_id]`."
            )
            raise typer.Exit(1)

        permissions = hosting.get_project_role_permissions(
            project_id=project_id, role_id=role_id, token=token
        )

        if as_json:
            console.print(json.dumps(permissions))
            return
        if permissions:
            headers = list(permissions[0].keys())
            table = [list(permission.values()) for permission in permissions]
            console.print(tabulate(table, headers=headers))
        else:
            # If returned empty list, print the empty
            console.print(str(permissions))
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise typer.Exit(1) from err


@project_cli.command(name="users")
def get_project_role_users(
    project_id: Optional[str] = typer.Option(
        None,
        help="The ID of the project. If not provided, the selected project will be used. If no project is selected, it throws an error.",
    ),
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """Retrieve the users for a project."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    try:
        if project_id is None:
            project_id = hosting.get_selected_project()
        if project_id is None:
            console.error(
                "no project_id provided or selected. Set it with `reflex cloud project users --project-id \\[project_id]`"
            )
            raise typer.Exit(1)

        users = hosting.get_project_role_users(project_id=project_id, token=token)

        if as_json:
            console.print(json.dumps(users))
            return
        if users:
            headers = list(users[0].keys())
            table = [list(user.values()) for user in users]
            console.print(tabulate(table, headers=headers))
        else:
            # If returned empty list, print the empty
            console.print(str(users))
    except NotAuthenticatedError as err:
        console.error("You are not authenticated. Run `reflex login` to authenticate.")
        raise typer.Exit(1) from err
