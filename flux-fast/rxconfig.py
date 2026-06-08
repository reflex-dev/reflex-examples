import reflex as rx

config = rx.Config(
    app_name="flux_fast",
    plugins=[
        rx.plugins.TailwindV3Plugin(),
        rx.plugins.RadixThemesPlugin(theme=rx.theme(accent_color="violet")),
    ],
)
