from sqlmodel import Field, SQLModel


class Follows(SQLModel, table=True):
    """A table of Follows. This is a many-to-many join table.

    See https://sqlmodel.tiangolo.com/tutorial/many-to-many/ for more information.
    """

    followed_username: str = Field(primary_key=True)
    follower_username: str = Field(primary_key=True)


class User(SQLModel, table=True):
    """A table of Users."""

    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str
    profile_photo: str = ""  # URL or path to profile photo
    bio: str = ""  # User bio/description
    display_name: str = ""  # Display name (different from username)
    location: str = ""  # User location
    website: str = ""  # User website


class Tweet(SQLModel, table=True):
    """A table of Tweets."""

    id: int | None = Field(default=None, primary_key=True)
    content: str
    created_at: str

    author: str


class Like(rx.Model, table=True):
    """A table of Likes. Tracks which users liked which tweets."""

    tweet_id: int = Field(primary_key=True)
    username: str = Field(primary_key=True)
