from typing import Optional
import reflex as rx
from .models import User, Contact


class State(rx.State):
    """The app state."""

    user: Optional[User] = None
