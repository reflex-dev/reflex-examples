import reflex as rx

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading(
                "Portfolio",
                size="lg",
                background_image="linear-gradient(271.68deg, #006FEE 0.75%, #00E075 88.52%)",
                background_clip="text",
                webkit_background_clip="text",
                color="transparent",
                font_weight="bold",
            ),
            rx.spacer(),
            rx.hstack(
                *[
                    rx.link(
                        text,
                        href=f"#{text.lower()}",
                        padding="2",
                        color="gray.600",
                        font_weight="medium",
                        _hover={
                            "color": "primary.500",
                            "transform": "translateY(-1px)",
                        },
                        _dark={
                            "color": "gray.300",
                            "_hover": {"color": "primary.200"},
                        },
                        transition="all 0.2s",
                    )
                    for text in ["About", "Projects", "Skills", "Contact"]
                ],
                rx.box(
                    rx.color_mode.button(
                        bg="transparent",
                        padding="3",
                        border_radius="lg",
                        _hover={
                            "bg": "primary.50",
                            "transform": "translateY(-1px)",
                        },
                        _dark={
                            "_hover": {"bg": "primary.900"},
                        },
                    ),
                    border="1px solid",
                    border_color="gray.200",
                    border_radius="lg",
                    _dark={"border_color": "gray.700"},
                ),
                spacing="6",
            ),
            width="100%",
            max_width="1200px",
            margin="0 auto",
            padding_x="4",
            padding_y="4",
        ),
        position="sticky",
        top="0",
        z_index="999",
        backdrop_filter="auto",
        backdrop_blur="12px",
        bg="rgba(255, 255, 255, 0.9)",
        _dark={"bg": "rgba(23, 25, 35, 0.9)"},
        border_bottom="1px solid",
        border_color="gray.100",
        _dark_border_color="gray.800",
    )
