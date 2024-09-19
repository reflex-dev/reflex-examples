"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from azure_auth.pages import callback, home, logout


class State(rx.State):
    """The app state."""

    ...


app = rx.App()
