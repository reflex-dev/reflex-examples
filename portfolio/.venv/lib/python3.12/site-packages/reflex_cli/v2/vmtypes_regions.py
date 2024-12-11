"""VMTypes and Regions commands for the Reflex Cloud CLI."""

import json
from typing import Optional

import typer
from tabulate import tabulate
from typing_extensions import Annotated

from reflex_cli import constants
from reflex_cli.utils import console

vm_types_regions_cli = typer.Typer()


@vm_types_regions_cli.command("vmtypes")
def get_vm_types(
    token: Optional[str] = typer.Option(None, help="The authentication token."),
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """Retrieve the available VM types."""
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    vmtypes = hosting.get_vm_types()
    if as_json:
        console.print(json.dumps(vmtypes))
        return
    if vmtypes:
        ordered_vmtpes = []
        for vmtype in vmtypes:
            ordered_vmtpes.append(
                {key: vmtype.get(key) for key in ["id", "name", "cpu", "ram"]}
            )
        headers = list(["id", "name", "cpu (cores)", "ram (gb)"])
        table = [list(vmtype.values()) for vmtype in ordered_vmtpes]
        console.print(tabulate(table, headers=headers))
    else:
        console.print(str(vmtypes))


@vm_types_regions_cli.command(name="regions")
def get_deployment_regions(
    loglevel: Annotated[
        constants.LogLevel, typer.Option(help="The log level to use.")
    ] = constants.LogLevel.INFO,
    as_json: bool = typer.Option(
        False, "-j", "--json", help="Whether to output the result in json format."
    ),
):
    """List all the regions of the hosting service.
    Areas available for deployment are:
    ams	Amsterdam, Netherlands
    arn	Stockholm, Sweden
    atl	Atlanta, Georgia (US)
    bog	Bogotá, Colombia
    bom	Mumbai, India
    bos	Boston, Massachusetts (US)
    cdg	Paris, France
    den	Denver, Colorado (US)
    dfw	Dallas, Texas (US)
    ewr	Secaucus, NJ (US)
    eze	Ezeiza, Argentina
    fra	Frankfurt, Germany
    gdl	Guadalajara, Mexico
    gig	Rio de Janeiro, Brazil
    gru	Sao Paulo, Brazil
    hkg	Hong Kong, Hong Kong
    iad	Ashburn, Virginia (US)
    jnb	Johannesburg, South Africa
    lax	Los Angeles, California (US)
    lhr	London, United Kingdom
    mad	Madrid, Spain
    mia	Miami, Florida (US)
    nrt	Tokyo, Japan
    ord	Chicago, Illinois (US)
    otp	Bucharest, Romania
    phx	Phoenix, Arizona (US)
    qro	Querétaro, Mexico
    scl	Santiago, Chile
    sea	Seattle, Washington (US)
    sin	Singapore, Singapore
    sjc	San Jose, California (US)
    syd	Sydney, Australia
    waw	Warsaw, Poland
    yul	Montreal, Canada
    yyz	Toronto, Canada.
    """
    from reflex_cli.utils import hosting

    console.set_log_level(loglevel)

    list_regions_info = hosting.get_regions()
    if as_json:
        console.print(json.dumps(list_regions_info))
        return
    if list_regions_info:
        headers = list(list_regions_info[0].keys())
        table = [list(deployment.values()) for deployment in list_regions_info]
        console.print(tabulate(table, headers=headers))
