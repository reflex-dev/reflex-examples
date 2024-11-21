import reflex as rx
from typing import Callable, Dict, List

from .style import DashboardStatBarStyle

statbarDataSet = {
    0: {
        "title": "USERS",
        "current_month": "14,482",
        "previous_month": "12,142",
        "delta": "+3.76%",
        "chart": [
            {"month": "January", "Users": 800},
            {"month": "February", "Users": 950},
            {"month": "March", "Users": 1200},
            {"month": "April", "Users": 1700},
            {"month": "May", "Users": 2200},
            {"month": "June", "Users": 2400},
            {"month": "July", "Users": 1500},
            {"month": "August", "Users": 1800},
            {"month": "September", "Users": 1100},
            {"month": "October", "Users": 1900},
            {"month": "November", "Users": 1700},
            {"month": "December", "Users": 2500},
        ],
    },
    1: {
        "title": "AVG. CLICK RATE",
        "current_month": "64,482",
        "previous_month": "32,142",
        "delta": "+52.76%",
        "chart": [
            {"month": "January", "Clicks": 5000},
            {"month": "February", "Clicks": 7000},
            {"month": "March", "Clicks": 9000},
            {"month": "April", "Clicks": 4000},
            {"month": "May", "Clicks": 6000},
            {"month": "June", "Clicks": 15000},
            {"month": "July", "Clicks": 18000},
            {"month": "August", "Clicks": 9000},
            {"month": "September", "Clicks": 6500},
            {"month": "October", "Clicks": 3000},
            {"month": "November", "Clicks": 12000},
            {"month": "December", "Clicks": 22000},
        ],
    },
    2: {
        "title": "SESSIONS",
        "current_month": "19,336",
        "previous_month": "21,642",
        "delta": "-4.24%",
        "chart": [
            {"month": "January", "Sessions": 300},
            {"month": "February", "Sessions": 600},
            {"month": "March", "Sessions": 1000},
            {"month": "April", "Sessions": 500},
            {"month": "May", "Sessions": 800},
            {"month": "June", "Sessions": 1500},
            {"month": "July", "Sessions": 2000},
            {"month": "August", "Sessions": 900},
            {"month": "September", "Sessions": 600},
            {"month": "October", "Sessions": 400},
            {"month": "November", "Sessions": 1800},
            {"month": "December", "Sessions": 500},
        ],
    },
    3: {
        "title": "SESSION DURATION",
        "current_month": "10m 23s",
        "previous_month": "6m 15s",
        "delta": "+57.60%",
        "chart": [
            {"month": "January", "Avg. Duration": 10},
            {"month": "February", "Avg. Duration": 40},
            {"month": "March", "Avg. Duration": 100},
            {"month": "April", "Avg. Duration": 15},
            {"month": "May", "Avg. Duration": 50},
            {"month": "June", "Avg. Duration": 200},
            {"month": "July", "Avg. Duration": 300},
            {"month": "August", "Avg. Duration": 100},
            {"month": "September", "Avg. Duration": 75},
            {"month": "October", "Avg. Duration": 25},
            {"month": "November", "Avg. Duration": 200},
            {"month": "December", "Avg. Duration": 120},
        ],
    },
}

statbarChart: Callable[[Dict[str, str]], rx.recharts.line_chart] = (
    lambda dataSet: rx.recharts.line_chart(
        rx.recharts.line(
            data_key=list(dataSet[0].keys())[1], type_="linear", dot=False
        ),
        data=dataSet,
        height="100%",
    )
)

statbarItemWrapper: Callable[[str, str, str, str, List[Dict[str, str]]], rx.hstack] = (
    lambda title, currentMonth, previousMonth, delta, data: rx.vstack(
        rx.vstack(
            rx.text(title, size="1", weight="bold", color=rx.color("slate", 11)),
            rx.text(currentMonth, size="6", weight="bold", color=rx.color("slate", 12)),
            spacing="2",
        ),
        rx.hstack(
            rx.badge(
                delta,
                color_scheme="grass" if list(delta)[0] == "+" else "ruby",
                size="1",
            ),
            rx.text(
                f"from {previousMonth}",
                size="1",
                weight="bold",
                color=rx.color("slate", 11),
            ),
            align="center",
        ),
        statbarChart(data),
        **DashboardStatBarStyle.itemWrapper,
    )
)

dashboardStatbar: Callable[[], rx.hstack()] = lambda: rx.hstack(
    *[
        statbarItemWrapper(
            item["title"],
            item["current_month"],
            item["previous_month"],
            item["delta"],
            item["chart"],
        )
        for item in statbarDataSet.values()
    ],
    **DashboardStatBarStyle.base,
)
