import reflex as rx

from .dashboardApp.main import dashboardApp

app = rx.App(theme=rx.theme(accent_color="violet", scaling="95%"))
app.add_page(dashboardApp(), route="/", title="Reflex Dashboard")
