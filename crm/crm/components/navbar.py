from crm.state import State, LoginState

import reflex as rx
import reflex.components.radix.themes as rdxt


def navbar():
    return rdxt.box(
        rx.hstack(
            rdxt.link(
                rdxt.heading("Reflex CRM", size="7", color_scheme="iris"),
                href="/",
                font_weight="medium",
            ),
            rx.hstack(
                rx.cond(
                    State.user,
                    rx.hstack(
                        rdxt.link(
                            "Log out",
                            color="blue.600",
                            on_click=LoginState.log_out,
                        ),
                        rdxt.avatar(
                            fallback=State.user.email,
                            size="4",
                            radius="full",
                            color_scheme="iris",
                        ),
                        spacing="1rem",
                    ),
                    rdxt.box(),
                )
            ),
            justify_content="space-between",
        ),
        width="100%",
        padding="1rem",
        margin_bottom="2rem",
        border_bottom="1px solid black",
    )
