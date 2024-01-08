"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import reflex as rx
from crm.pages import index, login
from crm.state import State


# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.add_page(login)
