import reflex as rx


class Base(rx.State):
    borders = {
        "tomato": "rgba(255, 99, 71, 0.71)",
        "red": "rgba(255, 0, 0, 0.71)",
        "ruby": "rgba(224, 17, 95, 0.71)",
        "crimson": "rgba(220, 20, 60, 0.71)",
        "pink": "rgba(255, 192, 203, 0.71)",
        "plum": "rgba(221, 160, 221, 0.71)",
        "purple": "rgba(128, 0, 128, 0.71)",
        "violet": "rgba(238, 130, 238, 0.71)",
        "iris": "rgba(90, 79, 207, 0.71)",
        "indigo": "rgba(75, 0, 130, 0.71)",
        "blue": "rgba(0, 0, 255, 0.71)",
        "cyan": "rgba(0, 255, 255, 0.71)",
        "teal": "rgba(0, 128, 128, 0.71)",
        "jade": "rgba(0, 168, 107, 0.71)",
        "green": "rgba(0, 128, 0, 0.71)",
        "grass": "rgba(124, 252, 0, 0.71)",
        "brown": "rgba(165, 42, 42, 0.71)",
        "orange": "rgba(255, 165, 0, 0.71)",
        "sky": "rgba(135, 206, 235, 0.71)",
        "mint": "rgba(189, 252, 201, 0.71)",
        "lime": "rgba(0, 255, 0, 0.71)",
        "yellow": "rgba(255, 255, 0, 0.71)",
        "amber": "rgba(255, 191, 0, 0.71)",
        "gold": "rgba(255, 215, 0, 0.71)",
        "bronze": "rgba(205, 127, 50, 0.71)",
        "gray": "rgba(128, 128, 128, 0.71)",
    }
    palette: list[list[str]] = [
        ["tomato", "surface", "not-used"],
        ["red", "surface", "not-used"],
        ["ruby", "surface", "not-used"],
        ["crimson", "surface", "not-used"],
        ["pink", "surface", "not-used"],
        ["plum", "surface", "not-used"],
        ["purple", "surface", "not-used"],
        ["violet", "surface", "not-used"],
        ["iris", "surface", "not-used"],
        ["indigo", "surface", "not-used"],
        ["blue", "surface", "not-used"],
        ["cyan", "surface", "not-used"],
        ["teal", "surface", "not-used"],
        ["jade", "surface", "not-used"],
        ["green", "surface", "not-used"],
        ["grass", "surface", "not-used"],
        ["brown", "surface", "not-used"],
        ["orange", "surface", "not-used"],
        ["sky", "surface", "not-used"],
        ["mint", "surface", "not-used"],
        ["lime", "surface", "not-used"],
        ["yellow", "surface", "not-used"],
        ["amber", "surface", "not-used"],
        ["gold", "surface", "not-used"],
        ["bronze", "surface", "not-used"],
        ["gray", "surface", "not-used"],
    ]
    category_name: str
    categories: list[dict[str, str]]
    selected_category: str
    current_label: str
