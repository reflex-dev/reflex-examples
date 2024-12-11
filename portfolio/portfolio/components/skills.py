import reflex as rx

def skill_card(title: str, skills: list[str]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                title,
                size="3",
                background_image="linear-gradient(271.68deg, #006FEE 0.75%, #00E075 88.52%)",
                background_clip="text",
                webkit_background_clip="text",
                color="transparent",
                font_weight="bold",
                margin_bottom="4",
            ),
            rx.flex(
                *[
                    rx.badge(
                        skill,
                        color_scheme="blue",
                        variant="soft",
                        padding="2",
                        border_radius="full",
                        font_weight="medium",
                        _hover={
                            "transform": "translateY(-2px)",
                            "bg": "blue.50",
                            "color": "blue.600",
                            "_dark": {
                                "bg": "blue.800",
                                "color": "blue.200",
                            },
                        },
                        transition="all 0.2s",
                    )
                    for skill in skills
                ],
                spacing="3",
                wrap="wrap",
            ),
            align="start",
            height="100%",
            spacing="4",
        ),
        padding="6",
        border="1px solid",
        border_color="gray.200",
        border_radius="xl",
        bg="white",
        _dark={
            "bg": "gray.800",
            "border_color": "gray.700",
        },
        _hover={
            "border_color": "blue.500",
            "transform": "translateY(-2px)",
            "box_shadow": "lg",
            "_dark": {
                "box_shadow": "dark-lg",
                "border_color": "blue.400",
            },
        },
        transition="all 0.2s",
    )

def skills() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Skills",
                size="1",
                background_image="linear-gradient(271.68deg, #006FEE 0.75%, #00E075 88.52%)",
                background_clip="text",
                webkit_background_clip="text",
                color="transparent",
                font_weight="bold",
                margin_bottom="2.5em",
                text_align="center",
            ),
            rx.grid(
                skill_card(
                    "Languages",
                    ["Python", "JavaScript", "TypeScript", "SQL", "HTML", "CSS"],
                ),
                skill_card(
                    "Frameworks",
                    ["React", "Next.js", "FastAPI", "Django", "Express"],
                ),
                skill_card(
                    "Tools & Technologies",
                    ["Git", "Docker", "AWS", "PostgreSQL", "Redis", "Linux"],
                ),
                template_columns="repeat(auto-fit, minmax(320px, 1fr))",
                gap="6",
                width="100%",
            ),
            width="100%",
            max_width="1200px",
            margin="0 auto",
            padding_x="4",
            padding_y="8em",
            spacing="8",
        ),
        width="100%",
        bg="radial-gradient(circle at center, blue.50 0%, transparent 70%)",
        _dark={"bg": "radial-gradient(circle at center, blue.900 0%, transparent 70%)"},
        id="skills",
    )
