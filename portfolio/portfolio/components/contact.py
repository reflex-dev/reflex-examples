import reflex as rx

def contact() -> rx.Component:
    return rx.vstack(
        rx.heading("Contact Me", size="2", margin_bottom="6"),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("email"),
                    rx.text("Email:"),
                    rx.link("john.doe@example.com", href="mailto:john.doe@example.com"),
                    width="100%",
                ),
                rx.hstack(
                    rx.icon("github"),
                    rx.text("GitHub:"),
                    rx.link("github.com/johndoe", href="https://github.com/johndoe", is_external=True),
                    width="100%",
                ),
                rx.hstack(
                    rx.icon("linkedin"),
                    rx.text("LinkedIn:"),
                    rx.link("linkedin.com/in/johndoe", href="https://linkedin.com/in/johndoe", is_external=True),
                    width="100%",
                ),
                spacing="4",
                padding="6",
            ),
            border="1px solid",
            border_color=rx.color_mode.current.border,
            border_radius="xl",
        ),
        padding_y="10",
        id="contact",
        width="100%",
    )
