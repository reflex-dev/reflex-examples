import reflex as rx


def layout(*children, size="2", **props):
    style = props.setdefault("style", {})
    style.setdefault("width", "100%")
    style.setdefault("> *", {"width": "100%"})
    return rx.container(
        rx.vstack(
            *children,
            **props,
        ),
        size=size,
    )
