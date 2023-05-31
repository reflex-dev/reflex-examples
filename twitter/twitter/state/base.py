"""Base state for Twitter example. Schema is inspired by https://drawsql.app/templates/twitter."""
from typing import Optional

from sqlmodel import Field

import pynecone as pc


class Follows(pc.Model, table=True):
    """A table of Follows. This is a many-to-many join table.

    See https://sqlmodel.tiangolo.com/tutorial/many-to-many/ for more information.
    """

    followed_username: str = Field(primary_key=True)
    follower_username: str = Field(primary_key=True)


class User(pc.Model, table=True):
    """A table of Users."""

    username: str = Field()
    password: str = Field()


class Tweet(pc.Model, table=True):
    """A table of Tweets."""

    content: str = Field()
    created_at: str = Field()

    author: str = Field()


class State(pc.State):
    """The base state for the app."""

    user: Optional[User] = None

    def logout(self):
        """Log out a user."""
        self.reset()
        return pc.redirect("/")

    def check_login(self):
        """Check if a user is logged in."""
        if not self.logged_in:
            return pc.redirect("/login")

    @pc.var
    def logged_in(self):
        """Check if a user is logged in."""
        return self.user is not None
