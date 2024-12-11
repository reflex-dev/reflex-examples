import reflex as rx

def navbar() -> rx.Component:
    return rx.hstack(
        rx.heading("Portfolio", size="4"),
        rx.spacer(),
        rx.hstack(
            rx.link("About", href="#about", padding="2"),
            rx.link("Projects", href="#projects", padding="2"),
            rx.link("Skills", href="#skills", padding="2"),
            rx.link("Contact", href="#contact", padding="2"),
            rx.color_mode.button(),
            spacing="4",
        ),
        width="100%",
        padding="4",
        position="sticky",
        top="0",
        z_index="999",
        bg=rx.color_mode.current.bg,
        border_bottom="1px solid",
        border_color=rx.color_mode.current.border,
    )
