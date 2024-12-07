from __future__ import annotations

import os
from typing import NamedTuple


class OtelConfig(NamedTuple):

    headers: str | None
    endpoint: str | None


def get_otel_config(
    tokens: dict[str, str],
) -> OtelConfig:
    otel_provider = tokens.get("OTEL_PROVIDER_TOKEN_NAME")
    match otel_provider:
        case "ARIZE_API_KEY":
            return OtelConfig(
                f"space_id={os.environ.get('ARIZE_SPACE_ID')},api_key={os.environ.get('ARIZE_API_KEY')}",
                "https://otlp.arize.com/v1",
            )

        case "PHOENIX_API_KEY":
            return OtelConfig(
                f"api_key={os.environ.get('PHOENIX_API_KEY')}",
                "https://app.phoenix.arize.com/v1/traces",
            )

        case "HYPERDX_API_KEY":
            return OtelConfig(
                f"api_key={os.environ.get('HYPERDX_API_KEY')}",
                "https://in-otel.hyperdx.io",
            )

        case _:
            print(
                "Invalid OTEL provider. Please set OTEL_PROVIDER environment variable",
            )
            return OtelConfig(None, None)
