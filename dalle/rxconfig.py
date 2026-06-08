import reflex as rx

config = rx.Config(
    app_name="dalle",
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                radius="medium",
                accent_color="mint",
            ),
        ),
    ],
)
