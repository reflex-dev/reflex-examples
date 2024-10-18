"""Constants related to hosting."""
import os
from types import SimpleNamespace

from reflex_cli.constants.base import Reflex


class ReflexHostingCli(SimpleNamespace):
    """Constants related to reflex-hosting-cli."""

    MODULE_NAME = "reflex-hosting-cli"


class Hosting(SimpleNamespace):
    """Constants related to hosting."""

    # The hosting config json file
    HOSTING_JSON = os.path.join(Reflex.DIR, "hosting_v0.json")
    # The hosting service backend URL
    CP_BACKEND_URL = os.environ.get(
        "CP_BACKEND_URL", "https://rxcp-prod-control-plane.fly.dev"
    )
    # The hosting service webpage URL
    CP_WEB_URL = os.environ.get("CP_WEB_URL", "https://control-plane.reflex.run")

    # The number of times to try and wait for the user to complete web authentication.
    WEB_AUTH_RETRIES = 60
    # The time to sleep between requests to check if for authentication completion. In seconds.
    WEB_AUTH_SLEEP_DURATION = 5
    # The time to wait for the reflex app sidecar to come up. In seconds.
    BACKEND_SIDECAR_WAIT_AND_PING_DURATION = 40
    # The number of iterations to try reflex app /ping endpoint and query logs printed from app.
    BACKEND_REFLEX_APP_PING_LOG_QUERY_RETRIES = 30
    # The time to wait for the frontend to come up after user initiates deployment. In seconds.
    FRONTEND_POLL_DURATION = 10


class RequirementsTxt(SimpleNamespace):
    """Requirements.txt constants."""

    # The requirements.txt file.
    FILE = "requirements.txt"

    # Number of unused packages for which we will throw a warning.
    UNUSED_WARN_THRESHOLD = 20
