import reflex as rx


config = rx.Config(
    app_name="counter",
    bun_path="$HOME/.bun/bin/bun",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
