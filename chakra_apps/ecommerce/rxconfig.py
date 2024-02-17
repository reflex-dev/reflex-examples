import reflex as rx

class EcommerceConfig(rx.Config):
    pass

config = EcommerceConfig(
    app_name="ecommerce",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)