import reflex as rx

def hero() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "John Doe",
                size="2xl",
                background_image="linear-gradient(271.68deg, #006FEE 0.75%, #00E075 88.52%)",
                background_clip="text",
                webkit_background_clip="text",
                color="transparent",
                font_weight="bold",
                font_size="5em",
                text_align="center",
            ),
            rx.text(
                "Full Stack Developer & Software Engineer",
                color="gray.600",
                font_size="xl",
                text_align="center",
                _dark={"color": "gray.300"},
            ),
            rx.text(
                "Building innovative solutions with modern technologies.",
                color="gray.500",
                font_size="lg",
                text_align="center",
                margin_top="1em",
                _dark={"color": "gray.400"},
            ),
            rx.hstack(
                rx.link(
                    rx.button(
                        "View Projects",
                        size="lg",
                        bg="primary.500",
                        color="white",
                        _hover={
                            "bg": "primary.600",
                            "transform": "translateY(-2px)",
                        },
                        _dark={
                            "bg": "primary.400",
                            "_hover": {"bg": "primary.500"},
                        },
                        transition="all 0.2s",
                    ),
                    href="#projects",
                ),
                rx.link(
                    rx.button(
                        "Contact Me",
                        size="lg",
                        variant="outline",
                        border_color="primary.500",
                        color="primary.500",
                        _hover={
                            "bg": "primary.50",
                            "transform": "translateY(-2px)",
                        },
                        _dark={
                            "color": "primary.200",
                            "border_color": "primary.200",
                            "_hover": {"bg": "primary.900"},
                        },
                        transition="all 0.2s",
                    ),
                    href="#contact",
                ),
                spacing="4",
                margin_top="2em",
            ),
            spacing="4",
            padding_y="8em",
            max_width="800px",
            margin="0 auto",
            width="100%",
        ),
        width="100%",
        bg="radial-gradient(circle at center, primary.50 0%, transparent 70%)",
        _dark={"bg": "radial-gradient(circle at center, primary.900 0%, transparent 70%)"},
    )
