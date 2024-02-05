from crm.state import State, LoginState
import reflex as rx


def navbar():
    return rx.chakra.box(
        rx.chakra.hstack(
            rx.chakra.link("Pyneknown", href="/", font_weight="medium"),
            rx.chakra.hstack(
                rx.cond(
                    State.user,
                    rx.chakra.hstack(
                        rx.chakra.link(
                            "Log out",
                            color="blue.600",
                            on_click=LoginState.log_out,
                        ),
                        rx.chakra.avatar(name=State.user.email, size="md"),
                        spacing="1rem",
                    ),
                    rx.chakra.box(),
                )
            ),
            justify_content="space-between",
        ),
        width="100%",
        padding="1rem",
        margin_bottom="2rem",
        border_bottom="1px solid black",
    )
