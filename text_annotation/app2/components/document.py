import reflex as rx

from ..states.base import Base
from ..states.document import DocumentState


def render_upload_area():
    return rx.upload(
        rx.text(
            "Click here to upload a file...",
            text_align="center",
            width="100%",
            height="100%",
        ),
        max_files=1,
        accept={
            "application/msword": [".doc"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
                ".docx"
            ],
        },
        id="upload",
        width="100%",
        height="100%",
        border_radius="8px",
        cursor="pointer",
    )


def render_upload_confirmation():

    def button(tag: str, name: str, color: str, func: callable):
        return rx.button(
            rx.icon(tag=tag, size=21),
            name,
            color_scheme=color,
            variant="surface",
            on_click=func,
            cursor="pointer",
        )

    return rx.vstack(
        rx.text(
            "Upload ",
            rx.chakra.span(rx.selected_files("upload"), as_="b"),
            " for annotation?",
            font_size="22px",
        ),
        rx.hstack(
            button(
                "file-up",
                "Upload",
                "grass",
                DocumentState.get_document(rx.upload_files(upload_id="upload")),
            ),
            button(
                "x",
                "Cancel Upload",
                "ruby",
                rx.clear_selected_files("upload"),
            ),
            justify_content="center",
        ),
        align_items="center",
        justify_content="center",
    )


def render_document():
    return rx.fragment(
        rx.center(
            rx.cond(
                rx.selected_files("upload"),
                render_upload_confirmation(),
                render_upload_area(),
            ),
            flex="60%",
            bg=rx.color_mode_cond(
                "#faf9fb",
                "#1a181a",
            ),
            border_radius="8px",
            width="100%",
            height="80vh",
            display=DocumentState.upload_ui,
        ),
        rx.hstack(
            rx.foreach(
                DocumentState.content,
                lambda data: rx.box(
                    rx.text(
                        f"{data[0]} ",
                        white_space="pre",
                        flex="0 1 auto",
                        border_bottom=f"2px solid {Base.borders[data[2]]}",
                    ),
                    padding="1em 0em",
                    on_mouse_down=DocumentState.highlight_start(data[1]),
                    on_mouse_up=DocumentState.highlight_end(data[1]),
                ),
            ),
            flex_wrap="wrap",
            overflow="hidden",
            flex="60%",
            display=DocumentState.document_ui,
            bg=rx.color_mode_cond(
                "#faf9fb",
                "#1a181a",
            ),
            border_radius="8px",
            padding="1em",
            width="100%",
            spacing="0",
        ),
        flex="60%",
    )
