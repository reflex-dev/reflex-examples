import reflex as rx

def project_card(title: str, description: str, tech_stack: list[str], github_url: str) -> rx.Component:
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
            ),
            rx.text(
                description,
                color="gray.600",
                _dark={"color": "gray.300"},
                margin_y="4",
            ),
            rx.wrap(
                *[
                    rx.badge(
                        tech,
                        color_scheme="blue",
                        variant="subtle",
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
                    for tech in tech_stack
                ],
                spacing="3",
                margin_y="4",
            ),
            rx.link(
                rx.button(
                    "View Project",
                    size="3",
                    variant="outline",
                    color_scheme="blue",
                    _hover={
                        "bg": "blue.50",
                        "transform": "translateY(-2px)",
                    },
                    _dark={
                        "color": "blue.200",
                        "border_color": "blue.200",
                        "_hover": {"bg": "blue.900"},
                    },
                    transition="all 0.2s",
                ),
                href=github_url,
                is_external=True,
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

def projects() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Projects",
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
        id="projects",
    )
