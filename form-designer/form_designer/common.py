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
        **props,
    )


def hstack(*children, **props):
    """Create a horizontal stack."""
    return stack(*children, direction="row", **props)


def vstack(*children, **props):
    """Create a vertical stack."""
    return stack(*children, direction="column", **props)