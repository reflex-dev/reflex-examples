import reflex as rx

config = rx.Config(
    app_name="quiz",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
