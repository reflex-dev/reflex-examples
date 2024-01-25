from crm.components import navbar
from crm.components import crm
from crm.state import State
import reflex as rx
import reflex.components.radix.primitives as rdxp
import reflex.components.radix.themes as rdxt


def index():
    return rx.vstack(
        navbar(),
        rx.cond(
            State.user,
            crm(),
            rx.vstack(
                rdxt.heading("Welcome to Reflex CRM!"),
                rdxt.text(
                    "This Reflex example demonstrates how to build a fully-fledged customer relationship management (CRM) interface."
                ),
                rdxt.link(
                    rdxt.button(
                        rx.lucide.icon(tag="lock", size=16),
                        "Log in to get started",
                        color_scheme="iris",
                        underline="none",
                    ),
                    href="/login",
                ),
                max_width="500px",
                text_align="center",
                spacing="1rem",
            ),
        ),
        spacing="1.5rem",
    )
