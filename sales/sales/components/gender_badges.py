import reflex as rx


def _badge(text: str, color_scheme: str):
    return rx.badge(
        text, color_scheme=color_scheme, radius="full", variant="soft", size="3"
    )


def gender_badge(gender: str):
    badge_mapping = {
        "Male": ("♂️ Male", "blue"),
        "Female": ("♀️ Female", "pink"),
        "Other": ("Other", "gray"),
    }
    return _badge(*badge_mapping.get(gender, ("Other", "gray")))
