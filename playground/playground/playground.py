import reflex as rx


@rx.page(route="/")
def test():
    return rx.text("playground")


app = rx.App()
