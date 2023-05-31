"""The state for the home page."""
from datetime import datetime

from sqlmodel import select

import pynecone as pc

from .base import Follows, State, Tweet, User


class HomeState(State):
    """The state for the home page."""

    tweet: str
    tweets: list[Tweet] = []

    friend: str
    search: str

    def post_tweet(self):
        """Post a tweet."""
        if not self.logged_in:
            return pc.window_alert("Please log in to post a tweet.")
        with pc.session() as session:
            tweet = Tweet(
                author=self.user.username,
                content=self.tweet,
                created_at=datetime.now().strftime("%m/%d %H"),
            )
            session.add(tweet)
            session.commit()
        return self.get_tweets()

    def get_tweets(self):
        """Get tweets from the database."""
        with pc.session() as session:
            if self.search:
                self.tweets = (
                    session.query(Tweet)
                    .filter(Tweet.content.contains(self.search))
                    .all()[::-1]
                )
            else:
                self.tweets = session.query(Tweet).all()[::-1]

    def set_search(self, search):
        """Set the search query."""
        self.search = search
        return self.get_tweets()

    def follow_user(self, username):
        """Follow a user."""
        with pc.session() as session:
            friend = Follows(
                follower_username=self.user.username, followed_username=username
            )
            session.add(friend)
            session.commit()

    @pc.var
    def following(self) -> list[Follows]:
        """Get a list of users the current user is following."""
        if self.logged_in:
            with pc.session() as session:
                return (
                    session.query(Follows)
                    .filter(Follows.follower_username == self.user.username)
                    .all()
                )
        return []

    @pc.var
    def followers(self) -> list[Follows]:
        """Get a list of users following the current user."""
        if self.logged_in:
            with pc.session() as session:
                return (
                    session.query(Follows)
                    .where(Follows.followed_username == self.user.username)
                    .all()
                )
        return []

    @pc.var
    def search_users(self) -> list[User]:
        """Get a list of users matching the search query."""
        if self.friend != "":
            with pc.session() as session:
                current_username = self.user.username if self.user is not None else ""
                users = (
                    session.query(User)
                    .filter(
                        User.username.contains(self.friend),
                        User.username != current_username,
                    )
                    .all()
                )
                return users
        return []
