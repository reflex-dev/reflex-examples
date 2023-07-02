import reflex as rx

class CollaborativecounterConfig(rx.Config):
    pass

config = CollaborativecounterConfig(
    app_name="collaborative_counter",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)