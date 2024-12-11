import reflex as rx

def project_card(title: str, description: str, tech_stack: list[str], link: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(title, size="lg"),
            rx.text(description),
            rx.wrap(
                *[
                    rx.badge(tech, variant="subtle", margin="1")
                    for tech in tech_stack
                ],
            ),
            rx.link(
                rx.button("View Project", variant="ghost"),
                href=link,
                is_external=True,
            ),
            spacing="4",
            padding="6",
        ),
        border="1px solid",
        border_color=rx.color_mode.current.border,
        border_radius="xl",
    )

def projects() -> rx.Component:
    return rx.vstack(
        rx.heading("Projects", size="xl", margin_bottom="6"),
        rx.grid(
            project_card(
                "Project 1",
                "A description of project 1 and its key features.",
                ["Python", "React", "PostgreSQL"],
                "https://github.com/username/project1",
            ),
            project_card(
                "Project 2",
                "A description of project 2 and its key features.",
                ["TypeScript", "Node.js", "MongoDB"],
                "https://github.com/username/project2",
            ),
            project_card(
                "Project 3",
                "A description of project 3 and its key features.",
                ["Python", "FastAPI", "Redis"],
                "https://github.com/username/project3",
            ),
            template_columns="repeat(auto-fit, minmax(300px, 1fr))",
            gap="4",
        ),
        padding_y="10",
        id="projects",
    )
