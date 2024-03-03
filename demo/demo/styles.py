"""Styles for the app."""
import reflex as rx

from .state import State

border_radius = "0.375rem"
box_shadow = "0px 0px 0px 1px rgba(84, 82, 95, 0.14)"
border = "1px solid #F4F3F6"
text_color = "black"
accent_text_color = "#1A1060"
accent_color = "#F5EFFE"
hover_accent_color = {"_hover": {"color": accent_color}}
hover_accent_bg = {"_hover": {"bg": accent_color}}
content_width_vw = "90vw"
sidebar_width = "20em"

template_page_style = {
    "padding_top": "5em",
    "padding_x": "2em",
}

template_content_style = {
    "width": rx.cond(
        State.sidebar_displayed,
        f"calc({content_width_vw} - {sidebar_width})",
        content_width_vw,
    ),
    "min-width": sidebar_width,
    "align_items": "flex-start",
    "box_shadow": box_shadow,
    "border_radius": border_radius,
    "padding": "1em",
    "margin_bottom": "2em",
}

link_style = {
    "color": text_color,
    "text_decoration": "none",
    **hover_accent_color,
}

overlapping_button_style = {
    "background_color": "white",
    "border": border,
    "border_radius": border_radius,
}

base_style = {
    rx.MenuButton: {
        "width": "3em",
        "height": "3em",
        **overlapping_button_style,
    },
    rx.MenuItem: hover_accent_bg,
}

tab_style = {
    "color": "#494369",
    "font_weight": 600,
    "_selected": {
        "color": "#5646ED",
        "bg": "#F5EFFE",
        "padding_x": "0.5em",
        "padding_y": "0.25em",
        "border_radius": "8px",
    },
}

ACCENT_BUTTON = {
    "justify_content": "center",
    "align_items": "center",
    "isolation": "isolate",
    "border_radius": 10,
    "font_style": "normal",
    "font_weight": 600,
    "color": "#F5EFFE",
    "background": "radial-gradient(82.06% 100% at 50% 100%, rgba(52, 46, 92, 0.8) 0%, rgba(234, 228, 253, 0) 100%), #7E69E0",
    "box_shadow": "0px 4px 10px -2px rgba(3, 3, 11, 0.32), 0px 4px 8px 0px rgba(3, 3, 11, 0.24), 0px 2px 3px 0px rgba(3, 3, 11, 0.10), 0px 0px 0px 1px rgba(32, 17, 126, 0.56), 0px -20px 12px -4px rgba(86, 70, 237, 0.32) inset, 0px 12px 12px -2px rgba(149, 128, 247, 0.16) inset, 0px 1px 0px 0px rgba(255, 255, 255, 0.16) inset;",
    "_hover": {
        "background": "radial-gradient(82.06% 100% at 50.00% 100.00%, rgba(52, 46, 92, 0.80) 0%, rgba(234, 228, 253, 0.00) 100%), #7E69E0);",
        "box_shadow": "0px 4px 10px -2px rgba(3, 3, 11, 0.12), 0px 4px 8px 0px rgba(3, 3, 11, 0.12), 0px 2px 3px 0px rgba(3, 3, 11, 0.10), 0px 0px 0px 2px rgba(149, 128, 247, 0.60), 0px -20px 12px -4px rgba(126, 105, 224, 0.60) inset, 0px 12px 12px -2px rgba(86, 70, 237, 0.12) inset, 0px 0px 0px 1px rgba(32, 17, 126, 0.40) inset;",
    },
}