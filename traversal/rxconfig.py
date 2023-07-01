import reflex as rx

config = rx.Config(
    app_name="traversal",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
