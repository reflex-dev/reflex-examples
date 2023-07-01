import reflex as rx


class TailwindConfig(rx.Config):
    pass


config = TailwindConfig(
    app_name="tailwind",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    tailwind={},
)
