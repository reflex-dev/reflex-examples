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
    HOSTING_JSON = os.path.join(Reflex.DIR, "hosting_v1.json")
    HOSTING_JSON_V0 = os.path.join(Reflex.DIR, "hosting_v0.json")
    # The hosting service backend URL
    HOSTING_SERVICE = os.environ.get(
        "CP_BACKEND_URL", "https://cloud-1e140ead-7b27-4248-961b-a58562714ac0.fly.dev"
    )
    # The hosting service webpage URL
    HOSTING_SERVICE_UI = os.environ.get("CP_WEB_URL", "https://cloud.reflex.dev")
    # The time to wait for HTTP requests to the backend
    TIMEOUT = 10
    # The number of times to retry authentication
    AUTH_RETRY_LIMIT = 5
    # How long to wait between retry attempts
    AUTH_RETRY_SLEEP_DURATION = 5

    # Aliases for compatibility with previous versions of Reflex
    CP_BACKEND_URL = HOSTING_SERVICE
    CP_WEB_URL = HOSTING_SERVICE_UI


class RequirementsTxt(SimpleNamespace):
    """Requirements.txt constants."""

    # The requirements.txt file.
    FILE = "requirements.txt"

    # Number of unused packages for which we will throw a warning.
    UNUSED_WARN_THRESHOLD = 20
