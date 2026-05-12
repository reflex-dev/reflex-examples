import reflex as rx

config = rx.Config(
    app_name="todo",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    plugins=[rx.plugins.RadixThemesPlugin()],
)
