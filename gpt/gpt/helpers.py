import reflex as rx


def navbar(State: rx.State) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.link(
                rx.flex(
                    rx.image(src="/favicon.ico"),
                    rx.heading("GPT Demo"),
                    align="center",
                ),
                href="/",
                color="black",
            ),
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(rx.icon("menu")),
                ),
                rx.menu.content(
                    rx.cond(
                        State.logged_in,
                        rx.fragment(
                            rx.flex(
                                rx.avatar(fallback=State.username[0].to(str), size="3"),
                                rx.text(State.username),
                                spacing="2",
                                align="center",
                                justify="center",
                            ),
                            rx.menu.separator(),
                        ),
                    ),
                    rx.menu.item(
                        "About GPT",
                        on_click=rx.redirect("https://openai.com/api/"),
                    ),
                    rx.cond(
                        State.logged_in,
                        rx.menu.item(
                            "Sign Out",
                            on_click=State.logout,
                        ),
                        rx.menu.item(
                            "Log In",
                            on_click=rx.redirect("/"),
                        ),
                    ),
                ),
            ),
            align="center",
            justify="between",
            border_bottom="0.2em solid #F0F0F0",
            padding="1em 2em",
            background="rgba(255,255,255, 0.90)",
        ),
        position="fixed",
        width="100%",
        top="0px",
        z_index="500",
    )
