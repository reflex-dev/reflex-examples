import reflex as rx

from .common import page


@page(
    route="/",
    title="Playground",
    description="Select an example from the drop down to get started.",
)
def test():
    return rx.fragment()


app = rx.App()
