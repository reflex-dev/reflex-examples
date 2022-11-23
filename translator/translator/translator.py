"""Welcome to Pynecone! This file outlines the steps to create a basic app."""

# Import pynecone.
from datetime import datetime
import googletrans

import pynecone as pc
from pynecone.base import Base

from .langs import langs


class Message(Base):
    original_text: str
    text: str
    created_at: str
    to_lang: str


class State(pc.State):
    """The app state."""

    text: str = ""
    messages: list[Message] = []
    lang: str = "de"

    @pc.var
    def output(self) -> str:
        if not self.text.strip():
            return "Translations will appear here."
        translator = googletrans.Translator()
        translation = translator.translate(self.text, dest=self.lang)
        return translation.text

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
    return pc.box(
        pc.text("Translator 🗺", font_size="2rem"),
        pc.text(
            "Translate things and post them as messages!",
            margin_top="0.5rem",
            color="#666",
        ),
    )


def down_arrow():
    return pc.box(
        "↓",
        color="#666",
        display="flex",
        margin_y="0.5rem",
        justify_content="center",
    )


def text_box(text):
    return pc.text(
        text,
        background_color="#fff",
        padding="1rem",
        border_radius="8px",
    )


def message(message):
    return pc.box(
        pc.vstack(
            text_box(message.original_text),
            down_arrow(),
            text_box(message.text),
            pc.box(
                f"{message.to_lang} · {message.created_at}",
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
    return pc.text(
        text,
        font_size="0.7rem",
        font_weight="bold",
        text_transform="uppercase",
        letter_spacing="0.05rem",
        **kwargs,
    )


def output():
    return pc.box(
        pc.box(
            smallcaps(
                "Output",
                color="#aeaeaf",
                background_color="white",
                padding_x="0.1rem",
            ),
            position="absolute",
            top="-0.5rem",
        ),
        pc.text(State.output),
        padding="1rem",
        border="1px solid #eaeaef",
        margin_top="1rem",
        border_radius="8px",
        position="relative",
    )


def index():
    """The main view."""
    return pc.container(
        header(),
        pc.input(
            placeholder="Text to translate",
            on_blur=State.set_text,
            margin_top="1rem",
            border_color="#eaeaef",
        ),
        pc.select(
            list(langs.keys()),
            value=State.lang,
            placeholder="Select a language",
            on_change=State.set_lang,
            margin_top="1rem",
        ),
        output(),
        pc.button("Post", on_click=State.post, margin_top="1rem"),
        pc.vstack(
            pc.foreach(State.messages, message),
            margin_top="2rem",
            spacing="1rem",
            align_items="left",
        ),
        padding="2rem",
        max_width="600px",
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Translator")
app.compile()
