import reflex as rx

# Define a vibrant gradient background
background_gradient = "linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #7E57C2)"

style = {
    "font_family": "Inter, sans-serif",
    "background": background_gradient,
    "min_height": "100vh",  # Ensure the gradient covers the full height of the viewport
    rx.avatar: {
        "border": "4px solid white",
        "box_shadow": "lg",
    },
    rx.button: {
        "width": "100%",
        "height": "3em",
        "padding": "0.5em 1em",
        "border_radius": "full",
        "color": "white",
        "background_color": "rgba(0, 0, 0, 0.5)",  # Semi-transparent black
        "backdrop_filter": "blur(10px)",
        "white_space": "nowrap",
        "box_shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
        "transition": "all 0.3s ease",
        "_hover": {
            "transform": "translateY(-2px)",
            "box_shadow": "0 6px 8px rgba(0, 0, 0, 0.15)",
            "background_color": "rgba(0, 0, 0, 0.7)",  # Darker on hover
        },
    },
    rx.link: {
        "text_decoration": "none",
        "_hover": {
            "text_decoration": "none",
        },
    },
    rx.vstack: {
        "background": "rgba(255, 255, 255, 0.9)",  # More opaque white background
        "backdrop_filter": "blur(20px)",
        "border_radius": "20px",
        "padding": "2em",
        "box_shadow": "0 8px 32px rgba(0, 0, 0, 0.1)",
        "color": "black",  # Ensure text is black for readability
        "align_items": "center",  # Center content horizontally
        "text_align": "center",  # Center text
    },
    rx.heading: {
        "color": "black",  # Ensure heading is black
        "margin_bottom": "0.5em",
    },
    rx.text: {
        "color": "black",  # Ensure text is black
        "margin_bottom": "1em",
    },
}
