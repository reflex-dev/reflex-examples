import reflex as rx
from sqlmodel import Field


class Follows(rx.Model, table=True):
    """A table of Follows. This is a many-to-many join table.

    See https://sqlmodel.tiangolo.com/tutorial/many-to-many/ for more information.
    """

    followed_username: str = Field(primary_key=True)
    follower_username: str = Field(primary_key=True)


class User(rx.Model, table=True):
    """A table of Users."""

    username: str
    password: bytes


class Tweet(rx.Model, table=True):
    """A table of Tweets."""

    content: str
    created_at: str

    author: str
