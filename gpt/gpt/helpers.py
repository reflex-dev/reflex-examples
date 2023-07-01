import reflex as rx


def navbar(State):
    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(rx.image(src="favicon.ico"), rx.heading("GPT Demo")), href="/"
            ),
            rx.menu(
                rx.menu_button(
                    rx.cond(
                        State.logged_in,
                        rx.avatar(name=State.username, size="md"),
                        rx.box(),
                    )
                ),
                rx.menu_list(
                    rx.center(
                        rx.vstack(
                            rx.avatar(name=State.username, size="md"),
                            rx.text(State.username),
                        )
                    ),
                    rx.menu_divider(),
                    rx.link(rx.menu_item("About GPT"), href="https://openai.com/api/"),
                    rx.link(rx.menu_item("Sign Out"), on_click=State.logout),
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
