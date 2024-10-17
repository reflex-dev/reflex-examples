import reflex as rx
from linkinbio.style import *

def link_button(name: str, url: str, icon: str) -> rx.Component:
    icon_map = {
        "globe": "globe",
        "twitter": "twitter",
        "github": "github",
        "linkedin": "linkedin",
    }
    icon_tag = icon_map.get(icon.lower(), "link")
    return rx.link(
        rx.button(
            rx.icon(tag=icon_tag),
            name,
            width="100%",
        ),
        href=url,
        is_external=True,
    )

def index() -> rx.Component:
    name = "Your Name"
    bio = "Your short bio here"
    avatar_url = "https://example.com/your-avatar.jpg"
    links = [
        {"name": "Website", "url": "https://example.com", "icon": "globe"},
        {"name": "Twitter", "url": "https://twitter.com/yourusername", "icon": "twitter"},
        {"name": "GitHub", "url": "https://github.com/yourusername", "icon": "github"},
        {"name": "LinkedIn", "url": "https://linkedin.com/in/yourusername", "icon": "linkedin"},
    ]

    return rx.center(
        rx.vstack(
            rx.avatar(src=avatar_url, size="2xl"),
            rx.heading(name, size="lg"),
            rx.text(bio),
            rx.vstack(
                rx.foreach(
                    links,
                    lambda link: link_button(link["name"], link["url"], link["icon"])
                ),
                width="100%",
                spacing="4",
            ),
            padding="8",
            max_width="400px",
            width="100%",
            spacing="6",
        ),
        width="100%",
        height="100vh",
        background="radial-gradient(circle, var(--chakra-colors-purple-100), var(--chakra-colors-blue-100))",
    )

app = rx.App(style=style)
app.add_page(index)