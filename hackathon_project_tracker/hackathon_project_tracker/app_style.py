from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import reflex as rx


@dataclass
class Style:
    """The style for the app."""
    dark: dict[str, str | rx.Component] = field(
        default_factory=lambda: {
            "background_color": "#121212",
        },
    )
