"""A container component."""
import reflex as rx
import reflex.components.radix.themes as rdxt

def container(*children, **props):
    """A fixed container based on a 960px grid."""
    # Enable override of default props.
    props = (
        dict(
            width="100%",
            max_width="960px",
            bg="white",
            height="100%",
            #px=[4, 12],
            px="9",

            margin="0 auto",
            position="relative",
        )
        | props
    )
    return rdxt.box(*children, **props)
