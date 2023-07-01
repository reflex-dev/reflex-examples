from crm.state import State, LoginState
import reflex as rx


def navbar():
    return rx.box(
        rx.hstack(
            rx.link("Pyneknown", href="/", font_weight="medium"),
            rx.hstack(
                rx.cond(
                    State.user,
                    rx.hstack(
                        rx.link(
                            "Log out",
                            color="blue.600",
                            on_click=LoginState.log_out,
                        ),
                        rx.avatar(name=State.user.email, size="md"),
                        spacing="1rem",
                    ),
                    rx.box(),
                )
            ),
            justify_content="space-between",
        ),
        width="100%",
        padding="1rem",
        margin_bottom="2rem",
        border_bottom="1px solid black",
    )
