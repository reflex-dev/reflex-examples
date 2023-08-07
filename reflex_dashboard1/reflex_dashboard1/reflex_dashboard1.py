"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from rxconfig import config

import reflex as rx
from reflex_icons.BootStrap import BsCalendar, BsCurrencyDollar, BsCreditCard
from reflex_icons import BootStrap
from typing import Union, List, Dict
from .components import line
from . import styles


class State(rx.State):
    """The app state."""

    display = True
    value: int = 3
    data: dict = {
        "labels": [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        "datasets": [
            {
                "label": "My Balance",
                "fill": False,
                "lineTension": 0.5,
                "backgroundColor": "#db86b2",
                "borderColor": "#B57295",
                "borderCapStyle": "butt",
                "borderDashOffset": 0.0,
                "borderJoinStyle": "#B57295",
                "pointBorderColor": "#B57295",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#B57295",
                "pointHoverBorderColor": "#B57295",
                "pointHoverBorderWidth": 2,
                "pointRadius": 1,
                "pointHitRadius": 10,
                "data": [
                    500,
                    300,
                    400,
                    500,
                    800,
                    650,
                    700,
                    690,
                    1000,
                    1200,
                    1050,
                    1300,
                ],
            },
        ],
    }

    def toggle(self):
        self.display = not self.display


def search_bar():
    return rx.input_group(
        rx.input_left_element(
            rx.icon(tag="search"),
            pointer_events="none",
        ),
        rx.input(type="number", placeholder="Search", border_radius="10px"),
        bg_color="#fff",
        mb=4,
        border="none",
        border_color="#fff",
        border_radius="10px",
        mr=2,
    )
    # return rx.hstack(
    #     rx.fragment(
    #         rx.icon(tag="search2", style=styles.NAV_SEARCH_STYLE),
    #         rx.text("Search", style=styles.NAV_SEARCH_STYLE, font_weight=400),
    #     ),
    #     rx.spacer(),
    #     rx.text("/", style=styles.NAV_SEARCH_STYLE),
    #     # on_click=NavbarState.change_search,
    #     display=["none", "flex", "flex", "flex", "flex"],
    #     min_width=["15em", "15em", "15em", "20em", "30em"],
    #     padding_x="1em",
    #     height="2em",
    #     border_radius="20px",
    #     bg="#FAF8FB",
    # )


def card_1() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.flex(
                    rx.text("Current Balance", color="gray.400"),
                    rx.text("$1,750.20", font_weight="bold"),
                    direction="column",
                ),
                rx.flex(BsCreditCard(mr=2), rx.text("Reflex."), align="center"),
                justify="space-between",
                w="100%",
                align="flex-start",
            ),
            rx.text("**** **** **** 1209", mb=4),
            rx.flex(
                rx.flex(
                    rx.flex(
                        rx.text(
                            "Valid Thru", text_transform="uppercase", font_size="xs"
                        ),
                        rx.text("12/25", font_size="lg"),
                        direction="column",
                        mr=4,
                    ),
                    rx.flex(
                        rx.text("CVV", text_transform="uppercase", font_size="xs"),
                        rx.text("***", font_size="lg"),
                        direction="column",
                        mr=4,
                    ),
                ),
                BootStrap.BsCreditCard(),
                align="flex-end",
                justify="space-between",
            ),
            p="1em",
            color="#fff",
            direction="column",
            h="100%",
            justify="space-between",
        ),
        border_radius="25px",
        mt=4,
        w="100%",
        h="200px",
        bg_gradient="linear(to-t, #B57295, #29259A)",
    )


def card_2() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.flex(
                    rx.text("Current Balance", color="gray.400"),
                    rx.text("$50,750.20", font_weight="bold"),
                    direction="column",
                ),
                rx.flex(
                    BootStrap.BsCreditCard(mr=2), rx.text("Reflex."), align="center"
                ),
                justify="space-between",
                w="100%",
                align="flex-start",
            ),
            rx.text("**** **** **** 9989", mb=4),
            rx.flex(
                rx.flex(
                    rx.flex(
                        rx.text(
                            "Valid Thru", text_transform="uppercase", font_size="xs"
                        ),
                        rx.text("12/27", font_size="lg"),
                        direction="column",
                        mr=4,
                    ),
                    rx.flex(
                        rx.text("CVV", text_transform="uppercase", font_size="xs"),
                        rx.text("***", font_size="lg"),
                        direction="column",
                        mr=4,
                    ),
                ),
                BootStrap.BsCreditCard(),
                align="flex-end",
                justify="space-between",
            ),
            p="1em",
            color="#fff",
            direction="column",
            h="100%",
            justify="space-between",
        ),
        border_radius="25px",
        mt=4,
        w="100%",
        h="200px",
        bg_gradient="linear(to-t, #D57295, #39259A)",
    )


def card_3() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.flex(
                    rx.text("Current Balance", color="gray.400"),
                    rx.text("$15,750.20", font_weight="bold"),
                    direction="column",
                ),
                rx.flex(
                    BootStrap.BsCreditCard(mr=2), rx.text("Reflex."), align="center"
                ),
                justify="space-between",
                w="100%",
                align="flex-start",
            ),
            rx.text("**** **** **** 1208", mb=4),
            rx.flex(
                rx.flex(
                    rx.flex(
                        rx.text(
                            "Valid Thru", text_transform="uppercase", font_size="xs"
                        ),
                        rx.text("11/23", font_size="lg"),
                        direction="column",
                        mr=4,
                    ),
                    rx.flex(
                        rx.text("CVV", text_transform="uppercase", font_size="xs"),
                        rx.text("***", font_size="lg"),
                        direction="column",
                        mr=4,
                    ),
                ),
                BootStrap.BsCreditCard(),
                align="flex-end",
                justify="space-between",
            ),
            p="1em",
            color="#fff",
            direction="column",
            h="100%",
            justify="space-between",
        ),
        border_radius="25px",
        mt=4,
        w="100%",
        h="200px",
        bg_gradient="linear(to-t, #C51195, #29222A)",
    )


def chart() -> rx.Component:
    return line(data=State.data, datasetIdKey="id")


def table_rows() -> rx.Component:
    return rx.fragment(
        rx.tr(
            rx.td(
                rx.flex(
                    rx.avatar(size="sm", mr=2, src="amazon.png"),
                    rx.flex(
                        rx.heading("Amazon", size="sm", letter_spacing="tight"),
                        rx.text("Apr 24, 2021 at 1:40pm", font_size="sm", color="gray"),
                        direction="column",
                    ),
                )
            ),
            rx.td("Electronic Devices"),
            rx.td("+2$", is_numeric=True),
            rx.td(
                rx.text("-$242", font_weight="bold", display="inline-table"),
                ".00",
                is_numeric=True,
            ),
        ),
        rx.tr(
            rx.td(
                rx.flex(
                    rx.avatar(size="sm", mr=2, src="youtube.jpeg"),
                    rx.flex(
                        rx.heading("Youtube", size="sm", letter_spacing="tight"),
                        rx.text("Apr 13, 2021 at 1:40pm", font_size="sm", color="gray"),
                        direction="column",
                    ),
                )
            ),
            rx.td("Social Media"),
            rx.td("+2$", is_numeric=True),
            rx.td(
                rx.text("-$242", font_weight="bold", display="inline-table"),
                ".00",
                is_numeric=True,
            ),
        ),
        rx.tr(
            rx.td(
                rx.flex(
                    rx.avatar(size="sm", mr=2, src="starbucks.png"),
                    rx.flex(
                        rx.heading("Starbucks", size="sm", letter_spacing="tight"),
                        rx.text("Apr 24, 2021 at 1:40pm", font_size="sm", color="gray"),
                        direction="column",
                    ),
                )
            ),
            rx.td("Cafe and restaurant"),
            rx.td("+2$", is_numeric=True),
            rx.td(
                rx.text("-$242", font_weight="bold", display="inline-table"),
                ".00",
                is_numeric=True,
            ),
        ),
    )


def index() -> rx.Component:
    return rx.flex(
        # column 1
        rx.flex(
            rx.flex(
                rx.flex(
                    rx.heading(
                        "Reflex",
                        mt=50,
                        mb=100,
                        font_size=[
                            "4xl",
                            "4xl",
                            "2xl",
                            "3xl",
                            "4xl",
                        ],
                        align_self="center",
                        letter_spacing="tight",
                    ),
                    rx.flex(
                        rx.flex(
                            rx.link(
                                BootStrap.BsHouse(class_name="active-icon"),
                                display=["none", "none", "flex", "flex", "flex"],
                            ),
                            rx.link(
                                rx.text("Home", class_name="active"),
                                _hover={"text_decor": "none"},
                                display=["flex", "flex", "none", "flex", "flex"],
                            ),
                            class_name="sidebar-items",
                        ),
                        rx.flex(
                            rx.link(
                                BootStrap.BsPieChart(font_size="2xl"),
                                display=["none", "none", "flex", "flex", "flex"],
                            ),
                            rx.link(
                                rx.text("Services"),
                                _hover={"text_decor": "none"},
                                display=["flex", "flex", "none", "flex", "flex"],
                            ),
                            class_name="sidebar-items",
                        ),
                        rx.flex(
                            rx.link(
                                BootStrap.BsCurrencyDollar(font_size="2xl"),
                            ),
                            rx.link(
                                rx.text("Credit"),
                                _hover={"text_decor": "none"},
                                display=["flex", "flex", "none", "flex", "flex"],
                            ),
                            class_name="sidebar-items",
                        ),
                        rx.flex(
                            rx.link(
                                BootStrap.BsBox(font_size="2xl"),
                                display=["none", "none", "flex", "flex", "flex"],
                            ),
                            rx.link(
                                rx.text("Wallet"),
                                _hover={"text_decor": "none"},
                                display=["flex", "flex", "none", "flex", "flex"],
                            ),
                            class_name="sidebar-items",
                            mr=[2, 6, 0, 0, 0],
                        ),
                        direction=["row", "row", "column", "column", "column"],
                        wrap=["wrap", "wrap", "nowrap", "nowrap", "nowrap"],
                        align="flex-start",
                        justify_content="center",
                    ),
                    rx.flex(
                        rx.avatar(my=2, src="avatar-5.png"),
                        rx.text("Masen Furer", text_align="center"),
                        direction="column",
                        align_items="center",
                        justify_content="space-between",
                        mb=10,
                        mt="15em",
                    ),
                    direction="column",
                    as_="nav",
                ),
                direction="column",
                justify_content="space-between",
                h=[None, None, "100vh"],
            ),
            w=["100%", "100%", "10%", "15%", "15%"],
            direction="column",
            align_items="center",
            bg="#282626",
            color="#fff",
        ),  # column 1 end
        # column 2
        rx.flex(
            rx.heading(
                "Welcome back, ",
                rx.flex("Masen", font_weight="bold", display="inline-flex"),
                font_weight="normal",
                mb=4,
                letter_spacing="tight",
            ),
            rx.text("My Balance", color="gray", font_size="sm"),
            rx.text("$5,900.30", font_weight="bold", font_size="2xl"),
            rx.flex(chart(), h="50vh"),
            rx.flex(
                rx.flex(
                    rx.heading(
                        "Transactions", as_="h2", size="lg", letterSpacing="tight"
                    ),
                    rx.text("Apr 2021", font_size="small", color="gray", ml=4),
                ),
                rx.icon_button(icon="bell"),
                justify_content="space-between",
                mt=8,
            ),
            rx.flex(
                rx.flex(
                    rx.table(
                        rx.thead(
                            rx.tr(
                                rx.th("Name of transaction"),
                                rx.th("Category"),
                                rx.th("Cashback", is_numeric=True),
                                rx.th("Amount", is_numeric=True),
                                color="gray",
                            )
                        ),
                        # table body
                        rx.tbody(table_rows(), rx.cond(State.display, table_rows())),
                        variant="unstyled",
                        mt=4,
                    ),
                    overflow="auto",
                ),
                rx.flex(
                    rx.divider(),
                    rx.cond(
                        State.display,
                        rx.icon(tag="chevron_up", on_click=State.toggle),
                        rx.icon(tag="chevron_down", on_click=State.toggle),
                    ),
                    rx.divider(),
                    align_content="center",
                ),
                direction="column",
            ),
            w=["100%", "100%", "60%", "60%", "55%"],
            p="3%",
            direction="column",
            overflow="auto",
            min_h="100vh",
        ),  # column 2 end
        # column 3
        rx.flex(
            rx.flex(
                search_bar(),
                rx.icon(
                    tag="bell",
                    font_size="3xl",
                    bg_color="#fff",
                    border_radius="50%",
                    p="7px",
                    ml="10px",
                ),
                rx.flex(
                    2,
                    w=8,
                    h=25,
                    bg_color="#B57295",
                    border_radius="50%",
                    color="#fff",
                    align="center",
                    justify="center",
                    ml=-3,
                    mt=-2,
                    z_index=100,
                    font_size="xs",
                ),
                align_content="center",
            ),
            rx.heading("My cards", letter_spacing="tight"),
            rx.cond(
                State.value == 1,
                card_1(),
                rx.cond(
                    State.value == 2,
                    card_2(),
                    rx.cond(State.value == 3, card_3()),
                ),
            ),
            rx.flex(
                rx.button(
                    bg_color=rx.cond(State.value == 1, "gray.600", "gray.400"),
                    on_click=State.set_value(1),
                    size="xs",
                    mx=1,
                ),
                rx.button(
                    bg_color=rx.cond(State.value == 2, "gray.600", "gray.400"),
                    on_click=State.set_value(2),
                    size="xs",
                    mx=1,
                ),
                rx.button(
                    bg_color=rx.cond(State.value == 3, "gray.600", "gray.400"),
                    on_click=State.set_value(3),
                    size="xs",
                    mx=1,
                ),
                justify_content="center",
                mt=2,
            ),
            rx.flex(
                rx.flex(
                    rx.text("Balance"),
                    rx.text("$140.42", font_weight="bold"),
                    justify="space-between",
                    mb=2,
                ),
                rx.flex(
                    rx.text("Credit Limit"),
                    rx.text("$150.42", font_weight="bold"),
                    justify="space-between",
                    mb=2,
                ),
                direction="column",
                my=4,
            ),
            rx.heading("Send money to", letter_spacing="tight", size="md", my=4),
            rx.flex(
                rx.avatar_group(
                    rx.avatar(src="avatar-2.jpg"),
                    rx.avatar(src="avatar-3.jpg"),
                    rx.avatar(src="avatar-4.jpg"),
                    rx.avatar(src="avatar-5.png"),
                    rx.avatar(src="avatar-2.jpg"),
                    size="md",
                    max=3,
                ),
                rx.avatar(
                    src="plus-1.png",  # TODO: revisit
                    ml=2,
                    p=3,
                    color="#fff",
                    bg_color="gray.300",
                ),
            ),
            rx.text("Card Number", color="gray", mt=10, mb=2),
            rx.input_group(
                rx.input_left_element(
                    BsCreditCard(color="gray.700"),
                    pointer_events="none",
                ),
                rx.input(type="number", placeholder="xxxx xxxx xxxx xxxx"),
            ),
            rx.text("Sum", color="gray", mt=10, mb=2),
            rx.input_group(
                rx.input_left_element(
                    BsCurrencyDollar(color="gray.700"),
                    pointer_events="none",
                ),
                rx.input(type="number", placeholder="130.00"),
            ),
            rx.button(
                "Send Money",
                mt=4,
                bg_color="blackAlpha.900",
                color="#fff",
                p={7},
                border_radius=15,
            ),
            w=["100%", "100%", "35%"],
            min_w=[None, None, "300px", "300px", "400px"],
            bg_color="#F5F5F5",
            p="3%",
            direction="column",
            overflow="auto",
        ),  # column 3 end
        h=[None, None, "100vh"],
        direction="row",
        overflow="hidden",
        max_width="2000px",
    )


# Add state and page to the app.
app = rx.App(stylesheets=["styles.css"])
app.add_page(index)
app.compile()
