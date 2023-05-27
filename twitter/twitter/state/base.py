"""Base state for Twitter example. Schema is inspired by https://drawsql.app/templates/twitter."""
from typing import Optional

from sqlmodel import Field, Relationship

import pynecone as pc


class Follows(pc.Model, table=True):
    """A table of Follows. This is a many-to-many join table.

    See https://sqlmodel.tiangolo.com/tutorial/many-to-many/ for more information.
    """

    followed_id: int = Field(foreign_key="user.id", primary_key=True)
    follower_id: int = Field(foreign_key="user.id", primary_key=True)


class User(pc.Model, table=True):
    """A table of Users."""

    username: str
    password: str

    tweets: list["Tweet"] = Relationship(back_populates="user")

    # The link is self-referencing, so we need to specify sa_relationship_kwargs.
    # See https://github.com/tiangolo/sqlmodel/issues/89 for more information.
    followers: list["User"] = Relationship(
        back_populates="followed",
        link_model=Follows,
        sa_relationship_kwargs=dict(
            primaryjoin="User.id==Follows.followed_id",
            secondaryjoin="User.id==Follows.follower_id",
        ),
    )
    followed: list["User"] = Relationship(
        back_populates="followers",
        link_model=Follows,
        sa_relationship_kwargs=dict(
            primaryjoin="User.id==Follows.follower_id",
            secondaryjoin="User.id==Follows.followed_id",
        ),
    )


class Tweet(pc.Model, table=True):
    """A table of Tweets."""

    content: str
    created_at: str

    user_id: int = Field(foreign_key=User.id)
    user: User = Relationship(back_populates="tweets")


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
