"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
from .base_state import State
from .pages import login, signup
from .home import home

app = pc.App(state=State)
app.add_page(login, route="/")
app.add_page(signup)
app.add_page(home)
app.compile()
