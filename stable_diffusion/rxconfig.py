import reflex as rx

class StablediffusionConfig(rx.Config):
    pass

config = StablediffusionConfig(
    app_name="stable_diffusion",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)