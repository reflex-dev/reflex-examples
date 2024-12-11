import reflex as rx

def contact() -> rx.Component:
    return rx.vstack(
        rx.heading(
            "Contact Me",
            size="2xl",
            background_image="linear-gradient(271.68deg, #006FEE 0.75%, #00E075 88.52%)",
            background_clip="text",
            webkit_background_clip="text",
            color="transparent",
            font_weight="bold",
            margin_bottom="2.5em",
            text_align="center",
        ),
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("mail"),
                    bg="blue.100",
                    color="blue.500",
                    padding="3",
                    border_radius="full",
                    _dark={
                        "bg": "blue.900",
                        "color": "blue.200",
                    },
                ),
                rx.text("Email:", font_weight="bold"),
                rx.link(
                    "john.doe@example.com",
                    href="mailto:john.doe@example.com",
                    color="blue.500",
                    _hover={"text_decoration": "underline"},
                    _dark={"color": "blue.200"},
                ),
                spacing="4",
            ),
            rx.hstack(
                rx.box(
                    rx.icon("github"),
                    bg="blue.100",
                    color="blue.500",
                    padding="3",
                    border_radius="full",
                    _dark={
                        "bg": "blue.900",
                        "color": "blue.200",
                    },
                ),
                rx.text("GitHub:", font_weight="bold"),
                rx.link(
                    "github.com/johndoe",
                    href="https://github.com/johndoe",
                    color="blue.500",
                    _hover={"text_decoration": "underline"},
                    _dark={"color": "blue.200"},
                ),
                spacing="4",
            ),
            rx.hstack(
                rx.box(
                    rx.icon("linkedin"),
                    bg="blue.100",
                    color="blue.500",
                    padding="3",
                    border_radius="full",
                    _dark={
                        "bg": "blue.900",
                        "color": "blue.200",
                    },
                ),
                rx.text("LinkedIn:", font_weight="bold"),
                rx.link(
                    "linkedin.com/in/johndoe",
                    href="https://linkedin.com/in/johndoe",
                    color="blue.500",
                    _hover={"text_decoration": "underline"},
                    _dark={"color": "blue.200"},
                ),
                spacing="4",
            ),
            spacing="6",
            padding="2em",
            max_width="600px",
            width="100%",
            margin="0 auto",
        ),
        padding_y="5em",
        width="100%",
        id="contact",
    )
