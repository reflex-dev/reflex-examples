import reflex as rx

def project_card(title: str, description: str, tech_stack: list[str], github_url: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                title,
                size="4",
                margin_bottom="0.5em",
            ),
            rx.text(
                description,
                color="gray.500",
                margin_bottom="1em",
            ),
            rx.flex(
                *[
                    rx.badge(
                        tech,
                        variant="soft",
                        bg="blue.100",
                        color="blue.900",
                        padding="2",
                        _hover={
                            "bg": "blue.200",
                            "transform": "scale(1.05)",
                        },
                        transition="all 0.2s",
                    )
                    for tech in tech_stack
                ],
                wrap="wrap",
                gap="2",
                margin_bottom="1em",
            ),
            rx.link(
                rx.button(
                    "View Project",
                    variant="ghost",
                    color="blue.500",
                    _hover={"bg": "blue.50"},
                    size="2",
                ),
                href=github_url,
                is_external=True,
            ),
            align_items="start",
            padding="2em",
        ),
        border="1px solid",
        border_color="gray.200",
        border_radius="xl",
        bg="white",
        transition="all 0.2s",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": "lg",
        },
        _dark={
            "bg": "gray.800",
            "border_color": "gray.700",
            "_hover": {
                "box_shadow": "dark-lg",
                "border_color": "blue.700",
            },
        },
    )

def projects() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Projects",
                size="1",
                background="linear-gradient(135deg, #006FEE 0%, #00E075 100%)",
                background_clip="text",
                webkit_background_clip="text",
                color="transparent",
                font_weight="900",
                margin_bottom="16",
                text_align="center",
                letter_spacing="-0.02em",
            ),
            rx.grid(
                project_card(
                    "Modern E-commerce Platform",
                    "A full-stack e-commerce solution with real-time inventory management, secure payments, and an intuitive admin dashboard.",
                    ["Python", "React", "PostgreSQL"],
                    "https://github.com/username/project1",
                ),
                project_card(
                    "Task Management System",
                    "A collaborative project management tool featuring real-time updates, task delegation, and detailed analytics dashboards.",
                    ["TypeScript", "Node.js", "MongoDB"],
                    "https://github.com/username/project2",
                ),
                project_card(
                    "AI-Powered Analytics",
                    "An intelligent analytics platform that processes and visualizes large datasets using machine learning algorithms.",
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
            padding_x="6",
            padding_y="32",
            spacing="8",
        ),
        width="100%",
        background="radial-gradient(circle at 50% 50%, rgba(0, 111, 238, 0.1) 0%, rgba(255, 255, 255, 0) 50%)",
        _dark={"background": "radial-gradient(circle at 50% 50%, rgba(0, 111, 238, 0.05) 0%, rgba(0, 0, 0, 0) 50%)"},
        id="projects",
    )
