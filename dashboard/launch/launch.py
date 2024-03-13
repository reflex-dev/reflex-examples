"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from rxconfig import config

import reflex as rx
from reflex.components.radix import themes as rdxt


def sidebar_link(text: str, href: str, icon: str) -> rx.Component:
    return rdxt.link(
        rdxt.flex(
            rdxt.icon_button(
                rdxt.icon(tag=icon),
                variant="soft",
            ),
            text,
            py="2",
            px="4",
            gap="4",
            align="baseline",
            direction="row",
            font_family="Share Tech Mono",
        ),
        href=href,
        width="100%",
        border_radius="8px",
        _hover={
            "background": "rgba(255, 255, 255, 0.1)",
            "backdrop_filter": "blur(10px)",
        },
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.image(src="/logo.jpg", height="28px", border_radius="8px"),
            rdxt.heading("REFLEX", font_family="Share Tech Mono", size="7"),
            width="100%",
            spacing="1em",
        ),
        rdxt.separator(width="100%", my="3"),
        rx.vstack(
            sidebar_link("Dashboard", "/", "bar_chart"),
            sidebar_link("Tools", "/tools", "gear"),
            sidebar_link("Team", "/team", "person"),
            padding_y="1em",
        ),
        width="250px",
        position="fixed",
        height="100%",
        left="0px",
        top="0px",
        align_items="left",
        z_index="10",
        backdrop_filter="blur(10px)",
        padding="2em",
    )


def navbar():
    return rx.hstack(
        rdxt.heading("Dashboard", font_family="Share Tech Mono", size="7"),
        rx.spacer(),
        rx.menu(
            rx.menu_button("Menu", font_family="Share Tech Mono"),
        ),
        position="fixed",
        width="calc(100% - 250px)",
        top="0px",
        z_index="1000",
        padding_x="2em",
        padding_top="2em",
        padding_bottom="1em",
        backdrop_filter="blur(10px)",
    )


def card(*children, **props):
    return rdxt.card(
        *children,
        box_shadow="rgba(0, 0, 0, 0.1) 0px 4px 6px -1px, rgba(0, 0, 0, 0.06) 0px 2px 4px -1px;",
        **props,
    )


def stat_card(title: str, stat, delta) -> rx.Component:
    color = "var(--red-9)" if delta[0] == "-" else "var(--green-9)"
    arrow = "decrease" if delta[0] == "-" else "increase"
    return card(
        rx.hstack(
            rx.vstack(
                rdxt.text(title),
                rx.stat(
                    rx.hstack(
                        rx.stat_number(stat, color=color),
                        rx.stat_help_text(rx.stat_arrow(type_=arrow), delta[1:]),
                    ),
                ),
            ),
        ),
    )


cards = [
    [
        "Today's Money",
        "$53,000",
        "+2%",
    ],
    [
        "Today's Users",
        "2,300",
        "+5%",
    ],
    [
        "Today's Orders",
        "1,400",
        "-3%",
    ],
    [
        "Today's Sales",
        "$23,000",
        "+2%",
    ],
]

data = [
    {"name": "Page A", "uv": 4000, "pv": 2400, "amt": 2400},
    {"name": "Page B", "uv": 3000, "pv": 1398, "amt": 2210},
    {"name": "Page C", "uv": 2000, "pv": 9800, "amt": 2290},
    {"name": "Page D", "uv": 2780, "pv": 3908, "amt": 2000},
    {"name": "Page E", "uv": 1890, "pv": 4800, "amt": 2181},
    {"name": "Page F", "uv": 2390, "pv": 3800, "amt": 2500},
    {"name": "Page G", "uv": 3490, "pv": 4300, "amt": 2100},
]

data01 = [
    {"name": "Group A", "value": 400, "fill": "var(--red-7)"},
    {"name": "Group B", "value": 300, "fill": "var(--green-7)"},
    {"name": "Group C", "value": 300, "fill": "var(--purple-7)"},
    {"name": "Group D", "value": 200, "fill": "var(--blue-7)"},
    {"name": "Group E", "value": 278, "fill": "var(--yellow-7)"},
    {"name": "Group F", "value": 189, "fill": "var(--pink-7)"},
]


def table1():
    return rdxt.table_root(
        rdxt.table_header(
            rdxt.table_row(
                rdxt.table_column_header_cell("Full name"),
                rdxt.table_column_header_cell("Email"),
                rdxt.table_column_header_cell("Group"),
            ),
        ),
        rdxt.table_body(
            rdxt.table_row(
                rdxt.table_row_header_cell("Danilo Sousa"),
                rdxt.table_cell("danilo@example.com"),
                rdxt.table_cell(rdxt.badge("Developer")),
            ),
            rdxt.table_row(
                rdxt.table_row_header_cell("Zahra Ambessa"),
                rdxt.table_cell("zahra@example.com"),
                rdxt.table_cell(rdxt.badge("Admin", variant="surface")),
            ),
            rdxt.table_row(
                rdxt.table_row_header_cell("Jasper Eriksson"),
                rdxt.table_cell("jasper@example.com"),
                rdxt.table_cell(rdxt.badge("Developer")),
            ),
        ),
    )


def graph1():
    return card(
        rx.recharts.line_chart(
            rx.recharts.line(
                data_key="pv",
                stroke="#8884d8",
            ),
            rx.recharts.line(
                data_key="uv",
                stroke="var(--accent-8)",
            ),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(),
            data=data,
            height=200,
        )
    )


def graph3():
    return card(
        rx.recharts.pie_chart(
            rx.recharts.pie(
                data=data01,
                data_key="value",
                name_key="name",
                cx="50%",
                cy="50%",
                label=True,
            ),
            height=200,
        )
    )


def graph2():
    return card(
        rx.recharts.area_chart(
            rx.recharts.area(data_key="uv", stroke="#8884d8", fill="#8884d8"),
            rx.recharts.area(data_key="pv", stroke="var(--accent-8)", fill="var(--accent-8)"),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(),
            data=data,
            height=400,
        )
    )


def content():
    return rx.grid(
        *[rx.grid_item(stat_card(*c), col_span=1, row_span=1) for c in cards],
        rx.grid_item(
            graph1(),
            col_span=3,
            row_span=2,
        ),
        rx.grid_item(graph3(), row_span=2, col_span=1),
        rx.grid_item(table1(), col_span=4, row_span=2),
        rx.grid_item(
            graph2(),
            col_span=3,
            row_span=2,
        ),
        rx.grid_item(col_span=2, bg="lightgreen"),
        rx.grid_item(col_span=2, bg="yellow"),
        rx.grid_item(col_span=4, bg="orange"),
        template_columns="repeat(4, 1fr)",
        width="100%",
        gap=4,
        row_gap=8,
    )


def index() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            navbar(),
            rx.box(
                content(),
                margin_top="calc(50px + 2em)",
                padding="2em",
            ),
            padding_left="250px",
        ),
        rdxt.theme_panel(),
        background_color="var(--accent-2)",
        font_family="Share Tech Mono",
        padding_bottom="4em",
    )


theme = rdxt.theme(
    appearance="light", has_background=True, radius="large", accent_color="iris"
)

# Create app instance and add index page.
app = rx.App(
    theme=theme,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap"
    ],
)
app.add_page(index)
