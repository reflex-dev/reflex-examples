"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
from crm.pages import index, login
from crm.state import State


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.add_page(login)
app.compile()
