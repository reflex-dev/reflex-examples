import reflex as rx

class DalleConfig(rx.Config):
    pass

config = DalleConfig(
    app_name="dalle",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
