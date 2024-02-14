import reflex as rx

config = rx.Config(
    app_name="translator",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
