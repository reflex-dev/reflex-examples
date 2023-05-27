"""The authentication state."""
import pynecone as pc

from .base import State, User


class AuthState(State):
    """The authentication state for sign up and login page."""

    username: str
    password: str
    confirm_password: str

    def signup(self):
        """Sign up a user."""
        with pc.session() as session:
            if self.password != self.confirm_password:
                return pc.window_alert("Passwords do not match.")
            if session.exec(User.select.where(User.username == self.username)).first():
                return pc.window_alert("Username already exists.")
            self.user = User(username=self.username, password=self.password)
            session.add(self.user)
            session.commit()
            return pc.redirect("/")

    def login(self):
        """Log in a user."""
        with pc.session() as session:
            user = session.exec(
                User.select.where(User.username == self.username)
            ).first()
            if user and user.password == self.password:
                self.user = user
                return pc.redirect("/")
            else:
                return pc.window_alert("Invalid username or password.")
