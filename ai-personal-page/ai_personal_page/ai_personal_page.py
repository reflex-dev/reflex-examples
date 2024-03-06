"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx


class State(rx.State):
    """The app state."""


text_size = "5"

def index() -> rx.Component:
    return rx.center(
        #rx.theme_panel(),
        rx.vstack(
            rx.heading("AI personal landing page", font_size="1.5em"),
            rx.hstack(
                rx.vstack(
                    rx.text("Welcome to Reflex! Providing insights about Reflex, think about innovating in python. Here are some quick links:", size=text_size), 
                    rx.unordered_list(
                        rx.list_item(
                            rx.flex(
                                rx.text("Website:", weight="bold"), 
                                rx.link("🔗 Reflex Site", href="https:reflex.dev",),
                                spacing="2",
                            ),
                        ),
                        rx.list_item(
                            rx.flex(
                                rx.text("Twitter:", weight="bold"), 
                                rx.link("🔗 @getreflex", href="https://twitter.com/getreflex",),
                                spacing="2",
                            ),
                        ),
                        rx.list_item(
                            rx.flex(
                                rx.text("Github:", weight="bold"), 
                                rx.link("🔗 reflex-dev / reflex", href="https://github.com/reflex-dev/reflex",),
                                spacing="2",
                            ),
                        ),
                        spacing="3",
                    ),
                    rx.text("Discover the power of Reflex with these commands:",),
                    rx.unordered_list(
                        rx.list_item(
                            rx.code("/resume"),
                        ),
                        rx.list_item(
                            rx.code("/facts"),
                        ),
                        spacing="3",
                    ),
                    rx.text("Ask a question about Reflex or explore some of the projects below:"),
                    rx.unordered_list(
                        rx.list_item(
                            rx.flex(
                                rx.link("🔗 Reflex Site", href="https:reflex.dev",),
                                spacing="2",
                            ),
                        ),
                        rx.list_item(
                            rx.flex(
                                rx.link("🔗 @getreflex", href="https://twitter.com/getreflex",),
                                spacing="2",
                            ),
                        ),
                        rx.list_item(
                            rx.flex(
                                rx.link("🔗 reflex-dev / reflex", href="https://github.com/reflex-dev/reflex",),
                                spacing="2",
                            ),
                        ),
                        spacing="3",
                    ),

                    width="65%",
                ),
                rx.container(
                    rx.image(src="favicon.ico", width="250px", height="auto", border_radius="1em",),
                    width="35%",
                ),
                spacing="7",
            ),
            
            width="70em",
            bg="white",
            padding="2em",
            align="center",
            border_radius="1em",
        ),
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 22% 11%, rgba(62, 180, 137, .40), hsla(0, 0%, 100%, 0) 19%), radial-gradient(circle at 82% 25%, rgba(33, 150, 243, .36), hsla(0, 0%, 100%, 0) 35%), radial-gradient(circle at 25% 61%, rgba(250, 128, 114, .56), hsla(0, 0%, 100%, 0) 55%)",
        
    )


# Add state and page to the app.
app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="medium", accent_color="mint"
    ),
    style={
        rx.text: {
            "font_size": "20px"
        },
        rx.link: {
            "font_size": "20px"
        },
        rx.code: {
            "font_size": "20px"
        }
    }
)
app.add_page(index)