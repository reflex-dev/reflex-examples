from typing import Callable
from .style import DashboardSideBarStyle

import reflex as rx

menuItemMap = {
    0: {"icon": "home", "name": "Dashboard"},
    1: {"icon": "users", "name": "Users"},
    2: {"icon": "contact", "name": "User Profile"},
    3: {"icon": "eye", "name": "Welcome"},
    4: {"icon": "file", "name": "Analytics"},
}

reflexLogoPath = [
    "M0 11.5999V0.399902H8.96V4.8799H6.72V2.6399H2.24V4.8799H6.72V7.1199H2.24V11.5999H0ZM6.72 11.5999V7.1199H8.96V11.5999H6.72Z",
    "M11.2 11.5999V0.399902H17.92V2.6399H13.44V4.8799H17.92V7.1199H13.44V9.3599H17.92V11.5999H11.2Z",
    "M20.16 11.5999V0.399902H26.88V2.6399H22.4V4.8799H26.88V7.1199H22.4V11.5999H20.16Z",
    "M29.12 11.5999V0.399902H31.36V9.3599H35.84V11.5999H29.12Z",
    "M38.08 11.5999V0.399902H44.8V2.6399H40.32V4.8799H44.8V7.1199H40.32V9.3599H44.8V11.5999H38.08Z",
    "M47.04 4.8799V0.399902H49.28V4.8799H47.04ZM53.76 4.8799V0.399902H56V4.8799H53.76ZM49.28 7.1199V4.8799H53.76V7.1199H49.28ZM47.04 11.5999V7.1199H49.28V11.5999H47.04ZM53.76 11.5999V7.1199H56V11.5999H53.76Z",
]


sidebarMenuHeader: Callable[[], rx.hstack] = lambda: rx.hstack(
    rx.el.svg(
        *[
            rx.el.svg.path(
                d=d,
                fill=rx.color_mode_cond("#110F1F", "white"),
            )
            for d in reflexLogoPath
        ],
        width="56",
        height="12",
        viewBox="0 0 56 12",
        fill="none",
        xmlns="http://www.w3.org/2000/svg",
    ),
    rx.badge(rx.text("Dashboard", size="1"), variant="surface", size="1"),
    align="center",
    width="100%",
)

sidebarMenuItem: Callable[[str, str], rx.hstack] = lambda icon, name: rx.hstack(
    rx.icon(tag=icon, size=14, color=rx.color("slate", 11)),
    rx.text(name, weight="medium", size="2", color=rx.color("slate", 11)),
    align="center",
    justify="start",
    height="28px",
)

dashboardSidebar: Callable[[], rx.vstack] = lambda: rx.vstack(
    sidebarMenuHeader(),
    rx.divider(height="1em", opacity="0"),
    *[sidebarMenuItem(item["icon"], item["name"]) for item in menuItemMap.values()],
    **DashboardSideBarStyle.base,
)
