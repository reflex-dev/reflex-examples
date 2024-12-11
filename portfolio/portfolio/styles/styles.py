"""Custom styles for the portfolio website."""
import reflex as rx

# Color schemes
ACCENT = "rgb(0, 122, 255)"
ACCENT_DARK = "rgb(10, 132, 255)"
BG_DARK = "rgb(20, 20, 20)"
BG_LIGHT = "rgb(250, 250, 250)"

# Gradients
GRADIENT = "linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%)"
GRADIENT_DARK = "linear-gradient(90deg, #1CB5E0 0%, #000851 100%)"

# Fonts
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

# Styles
BASE_STYLE = {
    "font_family": FONT_FAMILY,
    "background": BG_LIGHT,
    rx.Heading: {
        "font_family": FONT_FAMILY,
        "font_weight": "600",
    },
    rx.Button: {
        "background": ACCENT,
        "_hover": {"background": ACCENT_DARK},
        "font_weight": "500",
    },
    rx.Link: {
        "text_decoration": "none",
        "_hover": {"text_decoration": "underline"},
    },
}

# Component styles
navbar_style = dict(
    width="100%",
    padding="1.5rem",
    background="rgba(255, 255, 255, 0.8)",
    backdrop_filter="blur(10px)",
    border_bottom="1px solid rgba(0, 0, 0, 0.1)",
    position="fixed",
    z_index="999",
)

hero_style = dict(
    padding_top="8rem",
    padding_bottom="4rem",
    min_height="100vh",
    align_items="center",
    justify_content="center",
    text_align="center",
)

section_style = dict(
    padding_y="4rem",
    width="100%",
    min_height="100vh",
    align_items="center",
)

card_style = dict(
    padding="2rem",
    border_radius="1rem",
    border="1px solid rgba(0, 0, 0, 0.1)",
    background="white",
    _hover={"transform": "translateY(-5px)", "box_shadow": "lg"},
    transition="all 0.2s ease-in-out",
)

badge_style = dict(
    background=ACCENT,
    color="white",
    border_radius="full",
    padding_x="0.75rem",
    padding_y="0.25rem",
    font_size="0.875rem",
    font_weight="500",
    margin="0.25rem",
)

footer_style = dict(
    width="100%",
    padding="2rem",
    background=BG_DARK,
    color="white",
    text_align="center",
)

# Dark mode styles
DARK_THEME = {
    **BASE_STYLE,
    "background": BG_DARK,
    "color": "white",
    rx.Card: {
        "background": "rgba(255, 255, 255, 0.05)",
        "border": "1px solid rgba(255, 255, 255, 0.1)",
    },
}
