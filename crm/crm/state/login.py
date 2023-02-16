import pynecone as pc
from .models import User
from .state import State


class LoginState(State):
    """State for the login form."""

    email_field: str = ""
    password_field: str = ""

    def log_in(self):
        with pc.session() as sess:
            user = sess.exec(User.select.where(User.email == self.email_field)).first()
            if user and user.password == self.password_field:
                self.user = user
                return pc.redirect("/")
            else:
                return pc.window_alert("Wrong username or password.")

    def sign_up(self):
        with pc.session() as sess:
            user = sess.exec(User.select.where(User.email == self.email_field)).first()
            if user:
                return pc.window_alert(
                    "Looks like you’re already registered! Try logging in instead."
                )
            elif not self.email_field or not self.password_field:
                return pc.window_alert("Email and password cannot be empty")
            else:
                sess.expire_on_commit = False  # Make sure the user object is accessible. https://sqlalche.me/e/14/bhk3
                user = User(email=self.email_field, password=self.password_field)
                self.user = user
                sess.add(user)
                sess.commit()
                return pc.redirect("/")

    def log_out(self):
        self.user = None
        return pc.redirect("/")
