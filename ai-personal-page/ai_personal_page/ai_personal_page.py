"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import os
import reflex as rx
from reflex_chat import chat
from openai import OpenAI


class State(rx.State):
    """The app state."""
    chat_bool = False

    def chat_ai(self):
        self.chat_bool = not self.chat_bool


text_size = "5"

_client = None

class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str


def get_openai_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


assistant_id = os.getenv("ASSISTANT_ID")

# Checking if the API key is set properly
if not os.getenv("OPENAI_API_KEY"):
    raise Exception("Please set OPENAI_API_KEY environment variable.")

# Checking if the assistant key is set properly
if not os.getenv("ASSISTANT_ID"):
    raise Exception("Please set ASSISTANT_ID environment variable.")

thread = get_openai_client().beta.threads.create()


async def process(chat, question: str):
    """Get the response from the API.

    Args:
        form_data: A dict with the current question.
    """

    chat.messages.append({"role": "user", "content": question})

    # Clear the input and start the processing.
    chat.processing = True
    yield

    get_openai_client().beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )

    run = get_openai_client().beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id
    )

    # Periodically retrieve the Run to check status and see if it has completed
    while run.status != "completed":
        keep_retrieving_run = get_openai_client().beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )

        if keep_retrieving_run.status == "completed":
            break
        
        if keep_retrieving_run.status == "failed":
                chat.processing = False
                yield rx.window_alert("OpenAI Request Failed! Try asking again.")
                return

    # Retrieve messages added by the Assistant to the thread
    all_messages = get_openai_client().beta.threads.messages.list(thread_id=thread.id)
    answer_text = all_messages.data[0].content[0].text.value
    chat.messages.append({"role": "assistant", "content": answer_text})
    yield

    # Toggle the processing flag.
    chat.processing = False


def index() -> rx.Component:
    return rx.center(
        # rx.theme_panel(),
        rx.vstack(
            rx.hstack(
                rx.spacer(),
                rx.heading("AI personal landing page", font_size="1.5em"),
                rx.spacer(),
                rx.color_mode.icon(),
                rx.color_mode.switch(),
                width="100%",
            ),
            rx.cond(
                State.chat_bool,
                chat(process=process),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "Welcome to Reflex! Providing insights about Reflex, think about innovating in python. Here are some quick links:",
                            size=text_size,
                        ),
                        rx.unordered_list(
                            rx.list_item(
                                rx.text("Website: ", weight="bold"),
                                rx.link(
                                    "🔗 Reflex Site",
                                    href="https:reflex.dev",
                                ),
                                    
                            ),
                            rx.list_item(
                                rx.text("Twitter: ", weight="bold"),
                                rx.link(
                                    "🔗 @getreflex",
                                    href="https://twitter.com/getreflex",
                                ),
                                    
                            ),
                            rx.list_item(
                                rx.text("Github: ", weight="bold"),
                                rx.link(
                                    "🔗 reflex-dev / reflex",
                                    href="https://github.com/reflex-dev/reflex",
                                ),    
                            ),
                            spacing="2",
                        ),
                        rx.text(
                            "Discover the power of Reflex with these commands:",
                        ),
                        rx.unordered_list(
                            rx.list_item(
                                rx.code("/tell me about Reflex"),
                            ),
                            rx.list_item(
                                rx.code("/how do I install Reflex"),
                            ),
                            spacing="2",
                        ),
                        rx.text(
                            "Ask a personal AI assistant a question about Reflex or explore some of the projects below:"
                        ),
                        rx.unordered_list(
                            rx.list_item(
                                rx.link(
                                    "🔗 Reflex Site",
                                    href="https:reflex.dev",
                                ),
                            ),
                            rx.list_item(
                                rx.link(
                                    "🔗 @getreflex",
                                    href="https://twitter.com/getreflex",
                                ),
                            ),
                            rx.list_item(
                                rx.link(
                                    "🔗 reflex-dev / reflex",
                                    href="https://github.com/reflex-dev/reflex",
                                ),
                            ),
                            spacing="2",
                        ),
                        width="65%",
                    ),
                    rx.container(
                        rx.color_mode_cond(
                            rx.image(src="/logos/light/reflex.svg", height="4em"),
                            rx.image(src="/logos/dark/reflex.svg", height="4em"),
                        ),
                        width="35%",
                    ),
                    spacing="7",
                ),
            ),
            rx.button("Chat with AI", on_click=State.chat_ai, size="4", margin_top="12px"),
            rx.text("Powered by Reflex", size="3"),
            width="70em",
            background_color=rx.color("mauve", 1),
            padding="2em",
            align="center",
            border_radius="1em",
            margin_top="52px",
            margin_bottom="24px",
            margin_x="52px"
            
        ),
        
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 22% 11%, rgba(62, 180, 137, .40), hsla(0, 0%, 100%, 0) 19%), radial-gradient(circle at 82% 25%, rgba(33, 150, 243, .36), hsla(0, 0%, 100%, 0) 35%), radial-gradient(circle at 25% 61%, rgba(250, 128, 114, .56), hsla(0, 0%, 100%, 0) 55%)",
    )


# Add state and page to the app.
app = rx.App(
    theme=rx.theme(
        appearance="dark", has_background=True, radius="medium", accent_color="mint"
    ),
    style={
        rx.text: {"font_size": "15px"},
        rx.link: {"font_size": "15px"},
        rx.code: {"font_size": "15px"},
    },
)
app.add_page(index)
