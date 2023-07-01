import reflex as rx

config = rx.Config(
    app_name="chatroom",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
