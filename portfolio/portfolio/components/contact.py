import reflex as rx
from reflex.components.icons import IconButton
from reflex.components.icons.lucide import Mail, Github, Linkedin

def contact() -> rx.Component:
    return rx.vstack(
        rx.heading(
            "Contact Me",
            size="2",
            color="primary.500",
            margin_bottom="1.5em",
        ),
        rx.box(
            rx.vstack(
                *[
                    rx.hstack(
                        rx.box(
                            rx.icon(icon),
                            bg="primary.50",
                            color="primary.500",
                            padding="3",
                            border_radius="full",
                            _dark={
                                "bg": "primary.900",
                                "color": "primary.200",
                            },
                        ),
                        rx.text(label + ":", color="gray.600"),
                        rx.link(
                            value,
                            href=href,
                            color="primary.500",
                            _hover={"color": "primary.600"},
                        ),
                        width="100%",
                    )
                    for icon, label, value, href in [
                        (Mail, "Email", "john.doe@example.com", "mailto:john.doe@example.com"),
                        (Github, "GitHub", "github.com/johndoe", "https://github.com/johndoe"),
                        (Linkedin, "LinkedIn", "linkedin.com/in/johndoe", "https://linkedin.com/in/johndoe"),
                    ]
                ],
                spacing="6",
                padding="2em",
            ),
            border="1px solid",
            border_color="gray.200",
            border_radius="xl",
            bg="white",
            _dark={"bg": "gray.800"},
            width="100%",
            max_width="600px",
            margin="0 auto",
            transition="all 0.2s",
            _hover={"box_shadow": "lg"},
        ),
        padding_y="5em",
        width="100%",
        id="contact",
    )
