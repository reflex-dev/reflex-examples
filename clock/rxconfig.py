import reflex as rx

config = rx.Config(
    app_name="clock",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
