import reflex as rx

def skill_card(category: str, skills: list[str]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(category, size="3", margin_bottom="4"),
            rx.wrap(
                *[
                    rx.badge(
                        skill,
                        variant="subtle",
                        color_scheme="blue",
                        padding="2",
                        margin="1",
                    )
                    for skill in skills
                ],
                spacing="3",
            ),
            align_items="start",
            padding="6",
        ),
        border="1px solid",
        border_color=rx.color_mode.current.border,
        border_radius="xl",
        width="100%",
    )

def skills() -> rx.Component:
    return rx.vstack(
        rx.heading("Skills", size="2", margin_bottom="6"),
        rx.grid(
            skill_card(
                "Languages",
                ["Python", "JavaScript", "TypeScript", "SQL", "HTML", "CSS"]
            ),
            skill_card(
                "Frameworks",
                ["React", "Next.js", "FastAPI", "Django", "Express"]
            ),
            skill_card(
                "Tools & Technologies",
                ["Git", "Docker", "AWS", "PostgreSQL", "Redis", "Linux"]
            ),
            template_columns="repeat(auto-fit, minmax(300px, 1fr))",
            gap="4",
            width="100%",
        ),
        padding_y="10",
        id="skills",
        width="100%",
    )
