from typing import Callable, Dict

import reflex as rx


employeeDataSet: list[dict[str, str]] = [
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-4.png",
        "name": "Alice Skydancer",
        "job": "Engineer",
        "email": "alice.dancer@skynet.com",
        "rate": "34",
        "phone": "+1 213-555-0173",
    },
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-6.png",
        "name": "Frank Codebreaker",
        "job": "Developer",
        "email": "frank.breaker@code.io",
        "rate": "58",
        "phone": "+1 310-555-0192",
    },
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-7.png",
        "name": "Diana Windwalker",
        "job": "Architect",
        "email": "diana.walker@designs.org",
        "rate": "72",
        "phone": "+1 415-555-0124",
    },
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-11.png",
        "name": "Nina Seawatcher",
        "job": "Manager",
        "email": "nina.watcher@seaviews.org",
        "rate": "93",
        "phone": "+1 408-555-0165",
    },
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-9.png",
        "name": "Sara Cloudshaper",
        "job": "Engineer",
        "email": "sara.shaper@cloudtech.net",
        "rate": "50",
        "phone": "+1 323-555-0112",
    },
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-10.png",
        "name": "Tom Trailfinder",
        "job": "Designer",
        "email": "tom.finder@trails.net",
        "rate": "27",
        "phone": "+1 805-555-0147",
    },
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-12.png",
        "name": "Oliver Hillclimber",
        "job": "Developer",
        "email": "oliver.climb@hillcode.com",
        "rate": "65",
        "phone": "+1 909-555-0189",
    },
    {
        "avatar": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-8.png",
        "name": "Eli Stonecarver",
        "job": "Manager",
        "email": "eli.carver@stones.com",
        "rate": "88",
        "phone": "+1 626-555-0186",
    },
]


employeTableMenuItem: Callable[[str, str, str], rx.hstack] = (
    lambda name, tag, color: rx.hstack(
        rx.icon(tag=tag, size=14),
        rx.text(name, font_size="11px", color_scheme="gray"),
        color=color,
        width="100%",
        justify="start",
        align="center",
    )
)

emplyeeTableMenu: Callable[[], rx.menu.root] = lambda: rx.menu.root(
    rx.menu.trigger(
        rx.icon(tag="ellipsis", size=14, cursor="pointer"),
    ),
    rx.menu.content(
        rx.menu.item(employeTableMenuItem("Send message", "mails", "inherit")),
        rx.menu.item(employeTableMenuItem("Add note", "notepad-text", "inherit")),
        rx.menu.item(employeTableMenuItem("Terminate Contract", "trash-2", "red")),
        size="1",
    ),
)


employeeDataRow: Callable[[Dict[str, str]], rx.table.row] = lambda data: rx.table.row(
    rx.table.cell(
        rx.hstack(
            rx.avatar(src=data["avatar"], size="2", radius="full"),
            rx.vstack(
                rx.text(data["name"], font_size="12px", weight="medium"),
                rx.text(
                    data["job"],
                    color_scheme="gray",
                    font_size="10px",
                    weight="medium",
                ),
                spacing="0",
            ),
            align="center",
        ),
    ),
    rx.table.cell(
        rx.vstack(
            rx.text(data["email"], font_size="12px"),
            rx.text("Email", color_scheme="gray", font_size="10px"),
            spacing="0",
        )
    ),
    rx.table.cell(
        rx.text(data["phone"], color_scheme="gray", font_size="11px", weight="regular"),
    ),
    rx.table.cell(
        rx.vstack(
            rx.text(f"${data['rate']}.0/h", font_size="12px"),
            rx.text("Rate", font_size="10px", color_scheme="gray"),
            spacing="0",
        )
    ),
    rx.table.cell(
        rx.hstack(
            rx.button(
                rx.icon(tag="pencil", size=13, color="gray"),
                variant="ghost",
                cursor="pointer",
            ),
            emplyeeTableMenu(),
        ),
    ),
    width="100%",
    align="center",
    white_space="nowrap",
)


dashbaordEmployee: Callable[[], rx.table.root] = lambda: rx.table.root(
    rx.table.header(
        rx.table.row(
            rx.foreach(
                ["Employee", "Email", "Phone", "Rate (USD)", ""],
                lambda title: rx.table.column_header_cell(
                    rx.text(title, font_size="12px", weight="bold")
                ),
            )
        ),
    ),
    rx.table.body(
        *[employeeDataRow(data) for data in employeeDataSet],
    ),
    width="100%",
    variant="surface",
    size="2",
)
