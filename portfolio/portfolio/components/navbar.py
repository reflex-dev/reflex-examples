import reflex as rx

def navbar() -> rx.Component:
    return rx.hstack(
        rx.heading(
            "Portfolio",
            size="3",
            color="primary.500",
        ),
        rx.spacer(),
        rx.hstack(
            *[
                rx.link(
                    text,
                    href=f"#{text.lower()}",
                    padding="2",
                    color="gray.600",
                    _hover={"color": "primary.500"},
                    _dark={
                        "color": "gray.300",
                        "_hover": {"color": "primary.400"},
                    },
                    transition="all 0.2s",
                )
                for text in ["About", "Projects", "Skills", "Contact"]
            ],
            rx.color_mode.button(
                _hover={"bg": "primary.50"},
                _dark={
                    "_hover": {"bg": "primary.900"},
                },
            ),
            spacing="4",
        ),
        width="100%",
        max_width="1200px",
        margin="0 auto",
        padding="4",
        position="sticky",
        top="0",
        z_index="999",
        backdrop_filter="blur(10px)",
        bg="rgba(255, 255, 255, 0.8)",
        _dark={"bg": "rgba(26, 32, 44, 0.8)"},
        border_bottom="1px solid",
        border_color="gray.200",
    )
