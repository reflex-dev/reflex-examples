import reflex as rx


def navbar(State):
    return rx.chakra.box(
        rx.chakra.hstack(
            rx.chakra.link(
                rx.chakra.hstack(rx.chakra.image(src="favicon.ico"), rx.chakra.heading("GPT Demo")), href="/"
            ),
            rx.chakra.menu(
                rx.chakra.menu_button(
                    rx.cond(
                        State.logged_in,
                        rx.chakra.avatar(name=State.username, size="md"),
                        rx.chakra.box(),
                    )
                ),
                rx.chakra.menu_list(
                    rx.chakra.center(
                        rx.chakra.vstack(
                            rx.chakra.avatar(name=State.username, size="md"),
                            rx.chakra.text(State.username),
                        )
                    ),
                    rx.chakra.menu_divider(),
                    rx.chakra.link(rx.chakra.menu_item("About GPT"), href="https://openai.com/api/"),
                    rx.chakra.link(rx.chakra.menu_item("Sign Out"), on_click=State.logout),
                ),
            ),
            justify="space-between",
            border_bottom="0.2em solid #F0F0F0",
            padding_x="2em",
            padding_y="1em",
            bg="rgba(255,255,255, 0.90)",
        ),
        position="fixed",
        width="100%",
        top="0px",
        z_index="500",
    )
