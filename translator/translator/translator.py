"""Welcome to Reflex! This file outlines the steps to create a basic app."""

# Import reflex.
from datetime import datetime
from googletrans import Translator

import reflex as rx
from reflex.base import Base

from .langs import langs

trans = Translator()

class Message(Base):
    original_text: str
    text: str
    created_at: str
    to_lang: str


class State(rx.State):
    """The app state."""

    text: str = ""
    messages: list[Message] = []
    lang: str = "Chinese (Simplified)"

    @rx.var
    def output(self) -> str:
        if not self.text.strip():
            return "Translations will appear here."
        translated = trans.translate(self.text,dest=self.lang)
        return translated.text

    def post(self):
        self.messages = [
            Message(
                original_text=self.text,
                text=self.output,
                created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
                to_lang=self.lang,
            )
        ] + self.messages


# Define views.


def header():
    """Basic instructions to get started."""
    return rx.box(
        rx.text("Translator 🗺", font_size="2rem"),
        rx.text(
            "Translate things and post them as messages!",
            margin_top="0.5rem",
            color="#666",
        ),
    )


def down_arrow():
    return rx.vstack(
        rx.icon(
            tag="arrow_down",
            color="#666",
        )
    )


def text_box(text):
    return rx.text(
        text,
        background_color="#fff",
        padding="1rem",
        border_radius="8px",
    )


def message(message):
    return rx.box(
        rx.vstack(
            text_box(message.original_text),
            down_arrow(),
            text_box(message.text),
            rx.box(
                rx.text(message.to_lang),
                rx.text(" · ", margin_x="0.3rem"),
                rx.text(message.created_at),
                display="flex",
                font_size="0.8rem",
                color="#666",
            ),
            spacing="0.3rem",
            align_items="left",
        ),
        background_color="#f5f5f5",
        padding="1rem",
        border_radius="8px",
    )


def smallcaps(text, **kwargs):
    return rx.text(
        text,
        font_size="0.7rem",
        font_weight="bold",
        text_transform="uppercase",
        letter_spacing="0.05rem",
        **kwargs,
    )


def output():
    return rx.box(
        rx.box(
            smallcaps(
                "Output",
                color="#aeaeaf",
                background_color="white",
                padding_x="0.1rem",
            ),
            position="absolute",
            top="-0.5rem",
        ),
        rx.text(State.output),
        padding="1rem",
        border="1px solid #eaeaef",
        margin_top="1rem",
        border_radius="8px",
        position="relative",
    )


def index():
    """The main view."""
    return rx.container(
        header(),
        rx.input(
            placeholder="Text to translate",
            on_blur=State.set_text,
            margin_top="1rem",
            border_color="#eaeaef",
        ),
        rx.select(
            list(langs.keys()),
            value=State.lang,
            placeholder="Select a language",
            on_change=State.set_lang,
            margin_top="1rem",
        ),
        output(),
        rx.button("Post", on_click=State.post, margin_top="1rem"),
        rx.vstack(
            rx.foreach(State.messages, message),
            margin_top="2rem",
            spacing="1rem",
            align_items="left",
        ),
        padding="2rem",
        max_width="600px",
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index, title="Translator")
