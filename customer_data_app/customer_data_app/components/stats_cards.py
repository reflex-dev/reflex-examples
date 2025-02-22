import reflex as rx
from reflex.components.radix.themes.base import (
    LiteralAccentColor,
)

from ..backend.backend import State


def _arrow_badge(arrow_icon: str, percentage_change: float, arrow_color: str):
    return rx.badge(
        rx.icon(
            tag=arrow_icon,
            color=rx.color(arrow_color, 9),
        ),
        rx.text(
            f"{percentage_change}%",
            size="2",
            color=rx.color(arrow_color, 9),
            weight="medium",
        ),
        color_scheme=arrow_color,
        radius="large",
        align_items="center",
    )


def stats_card(
    stat_name: str,
    value: int,
    prev_value: int,
    percentage_change: float,
    icon: str,
    icon_color: LiteralAccentColor,
    extra_char: str = "",
) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.icon(
                            tag=icon,
                            size=22,
                            color=rx.color(icon_color, 11),
                        ),
                        rx.text(
                            stat_name,
                            size="4",
                            weight="medium",
                            color=rx.color("gray", 11),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.cond(
                        value > prev_value,
                        _arrow_badge("trending-up", percentage_change, "grass"),
                        _arrow_badge("trending-down", percentage_change, "tomato"),
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.hstack(
                    rx.heading(
                        f"{extra_char}{value:,}",
                        size="7",
                        weight="bold",
                    ),
                    rx.text(
                        f"from {extra_char}{prev_value:,}",
                        size="3",
                        color=rx.color("gray", 10),
                    ),
                    spacing="2",
                    align_items="end",
                ),
                align_items="start",
                justify="between",
                width="100%",
            ),
            align_items="start",
            width="100%",
            justify="between",
        ),
        size="3",
        width="100%",
        max_width="22rem",
    )


def stats_cards_group() -> rx.Component:
    return rx.flex(
        stats_card(
            "Total Customers",
            State.current_month_values.num_customers,
            State.previous_month_values.num_customers,
            State.customers_change,
            "users",
            "blue",
        ),
        stats_card(
            "Total Payments",
            State.current_month_values.total_payments,
            State.previous_month_values.total_payments,
            State.payments_change,
            "dollar-sign",
            "orange",
            "$",
        ),
        stats_card(
            "Total Delivers",
            State.current_month_values.num_delivers,
            State.previous_month_values.num_delivers,
            State.delivers_change,
            "truck",
            "ruby",
        ),
        spacing="5",
        width="100%",
        wrap="wrap",
        display=["none", "none", "flex"],
    )
