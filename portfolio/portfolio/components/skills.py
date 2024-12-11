import reflex as rx

def skill_card(title: str, skills: list[str]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                title,
                size="4",
                color="blue.500",
                margin_bottom="1em",
            ),
            rx.flex(
                *[
                    rx.badge(
                        skill,
                        variant="soft",
                        bg="blue.50",
                        color="blue.700",
                        padding="0.5em 1em",
                        font_size="sm",
                        _hover={
                            "bg": "blue.100",
                            "transform": "scale(1.05)",
                        },
                        transition="all 0.2s",
                    )
                    for skill in skills
                ],
                wrap="wrap",
                gap="3",
            ),
            align_items="start",
            padding="2em",
        ),
        border="1px solid",
        border_color="gray.200",
        border_radius="xl",
        bg="white",
        _dark={"bg": "gray.800"},
        width="100%",
    )

def skills() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Skills",
                size="1",
                background="linear-gradient(135deg, #006FEE 0%, #00E075 100%)",
                background_clip="text",
                webkit_background_clip="text",
                color="transparent",
                font_weight="900",
                margin_bottom="16",
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
            padding_x="6",
            padding_y="32",
            spacing="8",
        ),
        width="100%",
        background="radial-gradient(circle at 50% 50%, rgba(0, 111, 238, 0.1) 0%, rgba(255, 255, 255, 0) 50%)",
        _dark={"background": "radial-gradient(circle at 50% 50%, rgba(0, 111, 238, 0.05) 0%, rgba(0, 0, 0, 0) 50%)"},
        id="skills",
    )
