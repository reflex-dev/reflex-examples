import reflex as rx

color_palette = {
    "primary": {
        "50": "#e6f1fe",
        "100": "#cce3fd",
        "200": "#99c7fb",
        "300": "#66aaf9",
        "400": "#338ef7",
        "500": "#006FEE",
        "600": "#005bc4",
        "700": "#004493",
        "800": "#002e62",
        "900": "#001731",
    },
}

fonts = {
    "heading": "Inter",
    "body": "Inter",
}

theme = rx.theme(
    accent_color="blue",
    fonts=fonts,
    has_background=True,
    spacing_patterns={
        "1": "0.5rem",
        "2": "1rem",
        "3": "1.5rem",
        "4": "2rem",
        "5": "3rem",
    },
)
