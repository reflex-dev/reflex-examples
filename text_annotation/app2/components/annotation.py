import reflex as rx
from ..components.palette import render_palette
from ..states.base import Base
from ..states.palette import Palette


def item_subtitles(subtitle: str):
    return rx.text(subtitle, font_size="11px", weight="bold", opacity="0.81")


def item_wrapper(title: str, component: rx.Component):

    def item_title(title_: str):
        return rx.hstack(
            rx.text(title_, weight="bold"),
            rx.chakra.accordion_icon(),
            width="100%",
            justify_content="space-between",
        )

    return rx.chakra.accordion(
        rx.chakra.accordion_item(
            rx.chakra.accordion_button(item_title(title)),
            rx.chakra.accordion_panel(component),
        ),
        allow_toggle=True,
        width="100%",
        border="transparent",
        padding="0.5em 0em",
    )


def add_new_category():
    return rx.vstack(
        rx.vstack(
            item_subtitles("Select category color"),
            render_palette(),
            width="100%",
            spacing="1",
        ),
        rx.vstack(
            item_subtitles("Enter category name"),
            rx.input(
                value=Base.category_name, on_change=Base.set_category_name, width="100%"
            ),
            width="100%",
            spacing="1",
        ),
        rx.spacer(),
        rx.button(
            "Add Category",
            on_click=Palette.add_new_category,
            width="100%",
            size="2",
            cursor="pointer",
        ),
    )


def display_categories():
    return rx.hstack(
        rx.foreach(
            Base.categories,
            lambda data: rx.badge(
                data["name"],
                variant=data["type"],
                color_scheme=data["color"],
                size="3",
                cursor="pointer",
                on_click=Palette.select_category(data),
            ),
        ),
        width="100%",
        display="flex",
        flex_wrap="wrap",
    )


def render_annotation_panel():
    return rx.vstack(
        item_wrapper("Add Category", add_new_category()),
        item_wrapper("Categories", display_categories()),
        flex=["100%", "100%", "100%", "100%", "30%"],
        bg=rx.color_mode_cond(
            "#faf9fb",
            "#1a181a",
        ),
        border_radius="8px",
        padding="0.5em",
    )
