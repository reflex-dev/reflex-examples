"""The state for the home page."""
from datetime import datetime

from sqlmodel import select

import pynecone as pc

from .base import Follows, State, Tweet, User


class HomeState(State):
    """The state for the home page."""

    tweet: str
    show_tweet: bool = False
    tweets: list[Tweet] = []

    friend: str
    search: str

    def toggle_tweet(self):
        """Toggle the tweet modal."""
        self.show_tweet = not (self.show_tweet)
        return self.get_tweets()

    def post_tweet(self):
        """Post a tweet."""
        if not self.logged_in:
            return pc.window_alert("Please log in to post a tweet.")
        with pc.session() as session:
            tweet = Tweet(
                username=self.user.select().first().username,
                tweet=self.tweet,
                time=datetime.now().strftime("%m/%d %H"),
            )
            session.add(tweet)
            session.commit()
        return self.toggle_tweet()

    def get_tweets(self):
        """Get tweets from the database."""
        with pc.session() as session:
            if self.search != "":
                self.tweets = (
                    session.query(Tweet)
                    .filter(Tweet.tweet.contains(self.search))
                    .all()[::-1]
                )
            else:
                self.tweets = session.query(Tweet).all()[::-1]

    def set_search(self, search):
        """Set the search query."""
        self.search = search
        return self.get_tweets()

    def follow_user(self, user):
        """Follow a user."""
        with pc.session() as session:
            friend = Follows(username=self.username, friend=user)
            session.add(friend)
            session.commit()

    @pc.var
    def following(self) -> list[User]:
        """Get a list of users the current user is following."""
        if self.user is not None:
            return self.user.followed
        return []

    @pc.var
    def followers(self) -> list[User]:
        """Get a list of users following the current user."""
        if self.user is not None:
            return self.user.followers
        return []

    @pc.var
    def search_users(self) -> list[Follows]:
        """Get a list of users matching the search query."""
        if self.logged_in and self.friend != "":
            with pc.session() as session:
                users = session.exec(
                    select(User).where(
                        self.friend in User.username, User.username != self.username
                    )
                ).all()
                return users
        return []
