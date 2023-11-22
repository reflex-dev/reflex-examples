import reflex as rx
from .models import User
from .state import State


class LoginState(State):
    """State for the login form."""

    email_field: str = ""
    password_field: str = ""

    def log_in(self):
        with rx.session() as sess:
            user = sess.query(User).filter_by(email=self.email_field).first()
            if user and user.password == self.password_field:
                self.user = user
                return rx.redirect("/")
            else:
                return rx.window_alert("Wrong username or password.")

    def sign_up(self):
        with rx.session() as sess:
            user = sess.query(User).filter_by(email=self.email_field).first()
            if user:
                return rx.window_alert(
                    "Looks like you’re already registered! Try logging in instead."
                )
            else:
                sess.expire_on_commit = False  # Make sure the user object is accessible. https://sqlalche.me/e/14/bhk3
                user = User(email=self.email_field, password=self.password_field)
                self.user = user
                sess.add(user)
                sess.commit()
                return rx.redirect("/")

    def log_out(self):
        self.user = None
        return rx.redirect("/")
