from dataclasses import dataclass, field
from typing import Dict

import reflex as rx


@dataclass
class DashboardStatBarStyle:
    base: Dict[str, str] = field(
        default_factory=lambda: {
            "width": "100%",
            "display": "grid",
            "grid_template_columns": [
                f"repeat({i}, minmax(0, 1fr))" for i in [1, 1, 2, 2, 4, 4]
            ],
            "padding": "1em",
            "row_gap": "1em",
            "column_gap": "1em",
        }
    )

    itemWrapper: Dict[str, str] = field(
        default_factory=lambda: {
            "height": "180px",
            "flex": "1 1 300px",
            "border_radius": "8px",
            "position": "relative",
            "padding": "1em",
            "background": rx.color("gray", 2),
            "border": f"1px solid {rx.color('gray', 4)}",
        }
    )


DashboardStatBarStyle: DashboardStatBarStyle = DashboardStatBarStyle()
