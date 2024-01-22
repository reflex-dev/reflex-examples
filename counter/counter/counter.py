"""Welcome to Reflex! This file create a counter app."""
import reflex as rx
import reflex.components.radix.themes as rdxt
import random


class CountState(rx.State):
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
            rdxt.heading(CountState.count, size="9"),
            rx.hstack(
                rdxt.button(
                    "Decrement",
                    on_click=CountState.decrement,
                    background_color="red",
                    size="4",
                ),
                rdxt.button(
                    "Randomize",
                    on_click=CountState.random,
                    background_image="linear-gradient(90deg, rgba(255,0,0,1) 0%, rgba(0,176,34,1) 100%)",
                    size="4",
                ),
                rdxt.button(
                    "Increment",
                    on_click=CountState.increment,
                    background_color="green",
                    size="4",
                ),
            ),
            padding="1em",
            border_radius="1em",
            box_shadow="lg",
        ),
        padding_y="5em",
    )


app = rx.App(
    theme=rdxt.theme(
        appearance="light", has_background=True, radius="full", high_contrast=True,
    ),
)
app.add_page(index, title="Counter")
