import reflex as rx

from ...webui import styles
from ...webui.state import State


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon(
                    tag="hamburger",
                    mr=4,
                    on_click=State.toggle_drawer,
                    cursor="pointer",
                ),
                rx.breadcrumb(
                    rx.breadcrumb_item(
                        rx.heading("ReflexGPT", size="sm"),
                    ),
                    rx.breadcrumb_item(
                        rx.text(State.current_chat, size="sm", font_weight="normal"),
                    ),
                ),
            ),
            rx.hstack(
                rx.button(
                    "+ New chat",
                    bg=styles.accent_color,
                    px="4",
                    py="2",
                    h="auto",
                    on_click=State.toggle_modal,
                ),
                rx.menu(
                    rx.menu_button(
                        rx.avatar(name="User", size="md"),
                        bg="black",
                    ),
                    rx.menu_list(
                        rx.menu_item("Help"),
                        rx.menu_divider(),
                        rx.menu_item("Settings"),
                    ),
                ),
                spacing="8",
            ),
            justify="space-between",
        ),
        width="100%",
        backdrop_filter="auto",
        backdrop_blur="lg",
        p="4",
        border_bottom=f"1px solid {styles.border_color}",
        position="sticky",
        top="0",
        z_index="100",
    )
