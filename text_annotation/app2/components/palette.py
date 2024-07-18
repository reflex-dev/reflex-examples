import reflex as rx

from ..states.base import Base
from ..states.palette import Palette

TAGS = {
    "width": "100%",
    "display": "flex",
    "flex_wrap": "wrap",
    "justify_content": "start",
    "align_items": "center",
    "gap": "0.65em 0.65em",
    "padding_top": "0.5em",
    "padding_bottom": "0.5em",
}


def render_palette():
    return rx.hstack(
        rx.foreach(
            Base.palette,
            lambda color: rx.button(
                width="28px",
                height="28px",
                variant=color[1],
                color_scheme=color[0],
                radius="full",
                cursor="pointer",
                disabled=rx.cond(color[2] == "not-used", False, True),
                on_click=Palette.select_category_color(color),
            ),
        ),
        style=TAGS,
    )
