import pynecone as pc
from .base_state import State, User


class AuthState(State):
    password: str
    confirm_password: str

    def signup(self):
        """Sign up a user."""
        with pc.session() as session:
            if self.password != self.confirm_password:
                return pc.window_alert("Passwords do not match.")
            if session.exec(User.select.where(User.username == self.username)).first():
                return pc.window_alert("Username already exists.")
            user = User(username=self.username, password=self.password)
            session.add(user)
            session.commit()
            self.logged_in = True
            return pc.redirect("/home")

    def login(self):
        """Log in a user."""
        with pc.session() as session:
            user = session.exec(
                User.select.where(User.username == self.username)
            ).first()
            if user and user.password == self.password:
                self.logged_in = True
                return pc.redirect("/home")
            else:
                return pc.window_alert("Invalid username or password.")
