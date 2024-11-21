from dataclasses import dataclass, field
from typing import Dict

import reflex as rx


@dataclass
class DashboardTrafficBarStyle:
    base: Dict[str, str] = field(
        default_factory=lambda: {
            "height": "100%",
            "padding": "1em",
            "grid_column": ["span 1" if i >= 4 else "span 3" for i in range(6)],
            "border_radius": "8px",
            "background": rx.color("gray", 2),
            "border": f"1px solid {rx.color('gray', 4)}",
        },
    )


DashboardTrafficBarStyle: DashboardTrafficBarStyle = DashboardTrafficBarStyle()
