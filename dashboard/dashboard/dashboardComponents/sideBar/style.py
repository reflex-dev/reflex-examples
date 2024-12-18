from dataclasses import dataclass, field
from typing import Dict

import reflex as rx


@dataclass
class DashboardSideBarStyle:
    base: Dict[str, str] = field(
        default_factory=lambda: {
            "top": "0",
            "left": "0",
            "width": "280px",
            "max_width": "280px",
            "height": "100vh",
            "position": "sticky",
            "padding": "1em 2em",
            "background": rx.color("gray", 2),
            "border_right": f"1px solid {rx.color('gray', 4)}",
            "display": ["none" if i <= 3 else "flex" for i in range(6)],
        }
    )


DashboardSideBarStyle: DashboardSideBarStyle = DashboardSideBarStyle()
