"""Welcome to Reflex! This file create a counter app."""

import reflex as rx
import random


class State(rx.State):
    """The app state."""

    count = 0

    def increment(self):
        """Increment the count."""
        self.count += 1

    def decrement(self):
        """Decrement the count."""
        self.count -= 1

    def random(self):
        """Randomize the count."""
        self.count = random.randint(0, 100)


def index():
    """The main view."""
    return rx.center(
        rx.vstack(
            rx.heading(State.count),
            rx.hstack(
                rx.button("Decrement", on_click=State.decrement, color_scheme="red"),
                rx.button(
                    "Randomize",
                    on_click=State.random,
                    background_image="linear-gradient(90deg, rgba(255,0,0,1) 0%, rgba(0,176,34,1) 100%)",
                    color="white",
                ),
                rx.button("Increment", on_click=State.increment, color_scheme="green"),
            ),
            align="center",
            padding="1em",
            bg="#ededed",
            border_radius="1em",
        ),
        padding_y="5em",
        font_size="2em",
        text_align="center",
    )


app = rx.App()
app.add_page(index, title="Counter")
