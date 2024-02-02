import reflex as rx


def navbar():
    return rx.chakra.box(
        rx.chakra.hstack(
            rx.chakra.hstack(
                rx.chakra.image(src="/nba.png", width="50px"),
                rx.chakra.heading("NBA Data"),
                rx.chakra.flex(
                    rx.chakra.badge("2015-2016 Season", color_scheme="blue"),
                ),
            ),
            rx.chakra.menu(
                rx.chakra.menu_button(
                    "Menu", bg="black", color="white", border_radius="md", px=4, py=2
                ),
                rx.chakra.menu_list(
                    rx.chakra.link(rx.chakra.menu_item("Graph"), href="/"),
                    rx.chakra.menu_divider(),
                    rx.chakra.link(
                        rx.chakra.menu_item(
                            rx.chakra.hstack(rx.chakra.text("20Dataset"), rx.chakra.icon(tag="download"))
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
