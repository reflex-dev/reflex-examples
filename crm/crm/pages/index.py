from crm.components import navbar
from crm.components import crm
from crm.state import State
import pynecone as pc

def index():
    return pc.vstack(
        navbar(),
        pc.cond(
            State.user,
            crm(),
            pc.vstack(
                pc.heading("Welcome to Pyneknown!"),
                pc.text(
                    "This Pynecone example demonstrates how to build a fully-fledged customer relationship management (CRM) interface."
                ),
                pc.link(
                    pc.button(
                        "Log in to get started", color_scheme="blue", underline="none"
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
