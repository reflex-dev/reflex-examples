import reflex as rx

def hero() -> rx.Component:
    return rx.vstack(
        rx.heading("John Doe", size="1", margin_bottom="4"),
        rx.text(
            "Full Stack Developer & Software Engineer",
            margin_bottom="6",
        ),
        rx.hstack(
            rx.link(
                rx.button("View Projects"),
                href="#projects",
            ),
            rx.link(
                rx.button("Contact Me", variant="outline"),
                href="#contact",
            ),
            spacing="4",
        ),
        padding_y="20",
        spacing="4",
        align_items="center",
    )
