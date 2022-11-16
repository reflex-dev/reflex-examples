"""Welcome to Pynecone! This file outlines the steps to create a basic app."""

# Import pynecone.
from datetime import datetime
import pcconfig
import googletrans

import pynecone as pc
from pynecone.base import Base

docs_url = "https://pynecone.io/docs/getting-started/introduction"
title = "Welcome to Pynecone!"
filename = f"{pcconfig.APP_NAME}/{pcconfig.APP_NAME}.py"


class Message(Base):
    text: str
    created_at: str


class State(pc.State):
    """The app state."""

    text: str = ""

    messages: list[Message] = []

    @pc.var
    def output(self) -> str:
        if self.text.strip() == "":
            return "Translations will appear here."
        translator = googletrans.Translator()
        translation = translator.translate(self.text, dest="fr")
        return translation.text

    def post(self):
        self.messages = [
            Message(
                text=self.output,
                created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
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


def message(message):
    return pc.box(
        pc.vstack(
            pc.text(message.text, font_size="1.1rem"),
            pc.text(message.created_at, font_size="0.8rem", color="#666"),
            spacing="0.1rem",
            align_items="left",
        ),
        border="1px solid #eaeaef",
        padding="1rem",
        border_radius="8px",
    )


def smallcaps(text, **kwargs):
    return pc.text(
        text,
        font_size="0.7rem",
        font_weight="bold",
        background_color="white",
        padding_x="0.1rem",
        text_transform="uppercase",
        letter_spacing="0.05rem",
        **kwargs,
    )


def output():
    return pc.box(
        pc.box(
            smallcaps("Output", color="#aeaeaf"),
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
    return pc.box(
        header(),
        pc.input(
            placeholder="Text to translate",
            on_change=State.set_text,
            margin_top="1rem",
            border_color="#eaeaef",
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
        max_width="500px",
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title=title)
app.compile()
