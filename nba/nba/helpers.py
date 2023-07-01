import reflex as rx


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.image(src="/nba.png", width="50px"),
                rx.heading("NBA Data"),
                rx.flex(
                    rx.badge("2015-2016 Season", color_scheme="blue"),
                ),
            ),
            rx.menu(
                rx.menu_button(
                    "Menu", bg="black", color="white", border_radius="md", px=4, py=2
                ),
                rx.menu_list(
                    rx.link(rx.menu_item("Graph"), href="/"),
                    rx.menu_divider(),
                    rx.link(
                        rx.menu_item(
                            rx.hstack(rx.text("20Dataset"), rx.icon(tag="download"))
                        ),
                        href="https://media.geeksforgeeks.org/wp-content/uploads/nba.csv",
                    ),
                ),
            ),
            justify="space-between",
            border_bottom="0.2em solid #F0F0F0",
            padding_x="2em",
            padding_y="1em",
            bg="rgba(255,255,255, 0.97)",
        ),
        position="fixed",
        width="100%",
        top="0px",
        z_index="500",
    )
