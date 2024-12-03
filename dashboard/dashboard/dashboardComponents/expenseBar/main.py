import reflex as rx
from typing import Callable

from .style import DashboardExpenseBarStyle

expenseDataSet = [
    {"month": "Jan", "new": 45, "overdue": 12},
    {"month": "Feb", "new": 38, "overdue": 15},
    {"month": "Mar", "new": 50, "overdue": 8},
    {"month": "Apr", "new": 60, "overdue": 20},
    {"month": "May", "new": 70, "overdue": 10},
    {"month": "Jun", "new": 55, "overdue": 18},
    {"month": "Jul", "new": 48, "overdue": 25},
    {"month": "Aug", "new": 65, "overdue": 12},
    {"month": "Sep", "new": 58, "overdue": 16},
    {"month": "Oct", "new": 62, "overdue": 14},
    {"month": "Nov", "new": 50, "overdue": 22},
    {"month": "Dec", "new": 75, "overdue": 9},
]


dashboardExpensebar: Callable[[], rx.vstack] = lambda: rx.vstack(
    rx.vstack(
        rx.heading("Monthly Expenses", size="4", weight="bold"),
        rx.text("January - December 2024", size="1", color=rx.color("slate", 11)),
        spacing="1",
    ),
    rx.divider(height="1rem", opacity="0"),
    rx.recharts.bar_chart(
        rx.recharts.graphing_tooltip(
            label_style={"fontWeight": "700"}, item_style={"padding": "0px"}
        ),
        rx.recharts.cartesian_grid(horizontal=True, vertical=False),
        *[
            rx.recharts.bar(
                data_key=name,
                fill=rx.color("gray", 8) if index == 1 else rx.color("violet", 10),
            )
            for index, name in enumerate(["new", "overdue"])
        ],
        rx.recharts.x_axis(data_key="month", axis_line=False),
        data=expenseDataSet,
        height=300,
        bar_size=10,
        bar_gap=5,
        bar_category_gap="2%",
    ),
    rx.vstack(
        rx.heading("Expenses up by 5.2% this year", size="2", weight="bold"),
        rx.text(
            "Showing total expenses for the last 12 months",
            size="1",
            color=rx.color("slate", 11),
        ),
        spacing="1",
    ),
    **DashboardExpenseBarStyle.base,
)
