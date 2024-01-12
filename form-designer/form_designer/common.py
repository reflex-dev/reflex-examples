import reflex as rx
import reflex.components.radix.themes as rdxt


def stack(*children, direction="row", **props):
    """Create a Flex with 100% width and centered content with wrapping."""
    return rdxt.flex(
        *children,
        direction=direction,
        align=props.pop("align", "center"),
        justify=props.pop("justify", "center"),
        wrap=props.pop("wrap", "wrap"),
        width=props.pop("width", "100%"),
        gap=props.pop("gap", "3"),
        **props,
    )


def hstack(*children, **props):
    """Create a horizontal stack."""
    return stack(*children, direction="row", **props)


def vstack(*children, **props):
    """Create a vertical stack."""
    return stack(*children, direction="column", **props)


def link(*children, href: str, **props):
    """Create a link."""
    return rdxt.link(rx.next_link(*children, href=href, **props), as_child=True)


def color_mode_switch():
    return hstack(
        rdxt.icon(tag="sun"),
        rdxt.switch(
            checked=rx.color_mode == "dark",
            on_checked_change=rx.toggle_color_mode,
        ),
        rdxt.icon(tag="moon"),
        justify="end",
        position="absolute",
        top=0,
        p="2",
    )
