import reflex as rx
import os

DB_URL = os.getenv("DB_URL")

# Checking if the API key is set properly
if not os.getenv("DB_URL"):
    raise Exception("Please set DB_URL environment variable.")

config = rx.Config(
    app_name="customer_data_app",
    db_url=DB_URL
)
