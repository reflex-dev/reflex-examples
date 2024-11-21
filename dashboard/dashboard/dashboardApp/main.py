import reflex as rx
from typing import Callable

from .style import DashboardAppStyle

from ..dashboardComponents.sideBar.main import dashboardSidebar
from ..dashboardComponents.navBar.main import dashboardNavbar
from ..dashboardComponents.statBar.main import dashboardStatbar
from ..dashboardComponents.trafficBar.main import dashboardTrafficbar
from ..dashboardComponents.expenseBar.main import dashboardExpensebar
from ..dashboardComponents.employeeTable.main import dashbaordEmployee

dashboardContentArea: Callable[[], rx.vstack()] = lambda: rx.vstack(
    dashboardNavbar(),
    dashboardStatbar(),
    rx.hstack(
        dashboardTrafficbar(),
        dashboardExpensebar(),
        **DashboardAppStyle.trafficAndExpenses,
    ),
    rx.box(dashbaordEmployee(), width="100%", padding="1em"),
    **DashboardAppStyle.contentArea,
)

# ... Main app function here ...
dashboardApp: Callable[[], rx.hstack] = lambda: rx.hstack(
    # ... App side bar ...
    dashboardSidebar(),
    # ... App main content area ...
    dashboardContentArea(),
    # ... App style object ...
    **DashboardAppStyle.base,
)
