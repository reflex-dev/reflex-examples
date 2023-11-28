from typing import Optional
import reflex as rx
from .models import User


class State(rx.State):
    """The app state."""

    user: Optional[User] = None
