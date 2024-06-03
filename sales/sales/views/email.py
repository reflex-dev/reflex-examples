import reflex as rx
from ..backend.backend import State

def email_box():
    return rx.box(
        rx.scroll_area(
            rx.icon_button(
                rx.icon("copy"),
                variant="soft",
                color_scheme="gray",
                size="2",
                on_click=[rx.set_clipboard(State.email_content_data), rx._x.toast.info(
                    "Copied to clipboard")],
                cursor="pointer",
                position="absolute",
                bottom="1px",
                right="1px",
                z_index="10",
            ),
            rx.text(State.email_content_data, line_height="1.75"),
            type="auto",
            scrollbars="vertical",
            height="100%",
            position="relative",
        ),
        width="100%",
        height=["400px", "400px", "550px"]
    )


def options():
    return rx.vstack(
        rx.vstack(
            rx.heading(f"Length limit: {State.length}", size="5"),
            rx.slider(
                min=500,
                max=1500,
                default_value=1000,
                step=100,
                size="2",
                on_change=State.set_length,
            ),
            width="100%",
        ),
        rx.vstack(
            rx.heading("Tone", size="5"),
            rx.select(
                items=["Formal", "Casual", "Friendly", "Convincing", "Humble", "Urgent", "Humorous"],
                default_value="Formal",
                size="3",
                on_change=State.set_tone,
            ),
            width="100%",
        ),
        spacing="5",
        width="100%",
    )

def email_gen_ui():
    return rx.card(
        rx.flex(
            email_box(),
            rx.divider(),
            options(),
            flex_direction=["column-reverse", "column-reverse", "column-reverse", "column"],
            padding=["0.5em", "0.5em", "1em"],
            spacing="5",
        ),
        width=["100%", "100%", "100%", "40%"],
    ),


