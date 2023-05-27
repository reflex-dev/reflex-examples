"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc

from .pages import home, login, signup
from .state.base import State

app = pc.App(state=State)
app.add_page(login)
app.add_page(signup)
app.add_page(home, route="/", on_load=State.check_login)
app.compile()
