import reflex as rx

def footer() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("© 2024 John Doe. All rights reserved."),
            rx.hstack(
                rx.link("GitHub", href="https://github.com/johndoe", is_external=True),
                rx.link("LinkedIn", href="https://linkedin.com/in/johndoe", is_external=True),
                rx.link("Twitter", href="https://twitter.com/johndoe", is_external=True),
                spacing="4",
            ),
            padding_y="4",
            spacing="4",
        ),
        width="100%",
        border_top="1px solid",
        border_color=rx.color_mode.current.border,
    )
