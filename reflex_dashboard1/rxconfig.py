import reflex as rx


class ReflexdashboardConfig(rx.Config):
    pass


config = ReflexdashboardConfig(
    app_name="reflex_dashboard1",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    frontend_packages=[
        "chart.js",
        "react-chartjs-2",
        "react-icons",
    ],
)
