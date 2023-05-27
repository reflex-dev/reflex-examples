"""The home page. This file includes examples abstracting complex UI into smaller components."""
import pynecone as pc
from twitter.state.base import State
from twitter.state.home import HomeState

from ..components import container


def tab_button(name, href):
    """A tab switcher button."""
    return pc.link(
        pc.icon(tag="star", mr=2),
        name,
        display="inline-flex",
        align_items="center",
        py=3,
        px=6,
        href=href,
        border="1px solid #eaeaea",
        font_weight="semibold",
        border_radius="full",
    )


def tabs():
    """The tab switcher displayed on the left."""
    return pc.box(
        pc.vstack(
            pc.heading("PySocial", size="md"),
            tab_button("Home", "/"),
            pc.box(
                pc.heading("Followers", size="sm"),
                pc.foreach(
                    HomeState.followers,
                    lambda friend: pc.vstack(
                        pc.hstack(
                            pc.avatar(name=friend.username, size="sm"),
                            pc.text(friend.username),
                        ),
                        padding="1em",
                    ),
                ),
                p=4,
                border_radius="md",
                border="1px solid #eaeaea",
            ),
            pc.button("Sign out", on_click=State.logout),
            align_items="left",
            gap=4,
        ),
        py=4,
    )


def sidebar(HomeState):
    """The sidebar displayed on the right."""
    return pc.vstack(
        pc.input(on_change=HomeState.set_search, placeholder="Search", width="100%"),
        pc.input(
            on_change=HomeState.set_friend,
            placeholder="Add friend",
            width="100%",
        ),
        pc.foreach(
            HomeState.search_users,
            lambda friend: pc.vstack(
                pc.hstack(
                    pc.avatar(name=friend.username, size="sm"),
                    pc.text(friend.username),
                    pc.spacer(),
                    pc.button(
                        pc.icon(tag="add", color="white", height="1em"),
                        on_click=lambda: HomeState.follow_user(friend.username),
                        bg="rgb(29, 161, 242)",
                    ),
                    width="100%",
                ),
                padding="1em",
                width="100%",
            ),
        ),
        pc.box(
            pc.heading("Following", size="sm"),
            pc.foreach(
                HomeState.following,
                lambda friend: pc.vstack(
                    pc.hstack(
                        pc.avatar(name=friend.friend, size="sm"),
                        pc.text(friend.friend),
                    ),
                    padding="1em",
                ),
            ),
            p=4,
            border_radius="md",
            border="1px solid #eaeaea",
            w="100%",
        ),
        align_items="start",
        gap=4,
        h="100%",
        py=4,
    )


def feed_header(HomeState):
    """The header of the feed."""
    return pc.hstack(
        pc.heading("Home", size="md"),
        pc.icon(
            tag="repeat",
            height="1.5em",
            width="1.5em",
            color="#676767",
            on_click=HomeState.get_tweets,
        ),
        justify="space-between",
        p=4,
        border_bottom="1px solid #ededed",
    )


def composer(HomeState):
    """The composer for new tweets."""
    return pc.grid(
        pc.vstack(
            pc.avatar(name=State.user.name, size="md"),
            p=4,
        ),
        pc.box(
            pc.text_area(
                w="100%",
                border=0,
                placeholder="What's happening?",
                resize="none",
                py=4,
                px=0,
                _focus={"border": 0, "outline": 0, "boxShadow": "none"},
                on_blur=HomeState.set_tweet,
            ),
            pc.hstack(
                pc.button(
                    "Tweet",
                    on_click=HomeState.post_tweet,
                    bg="rgb(29 161 242)",
                    color="white",
                    border_radius="full",
                ),
                justify_content="flex-end",
                border_top="1px solid #ededed",
                px=4,
                py=2,
            ),
        ),
        grid_template_columns="1fr 5fr",
        border_bottom="1px solid #ededed",
    )


def tweet(tweet):
    """Display for an individual tweet in the feed."""
    return pc.vstack(
        pc.hstack(
            pc.avatar(name=tweet.user.username, size="sm"),
            pc.text("@" + tweet.user.username),
            pc.spacer(),
            pc.text(tweet.time),
            width="100%",
            align_items="left",
        ),
        pc.divider(),
        pc.text(tweet.tweet, width="100%"),
        padding="1em",
        border_color="1px solid #ededed",
        border_width="1px",
        border_radius="lg",
        shadow="sm",
        width="100%",
    )


def feed(HomeState):
    """The feed."""
    return pc.box(
        feed_header(HomeState),
        composer(HomeState),
        pc.foreach(
            HomeState.tweets,
            tweet,
        ),
        border_x="1px solid #ededed",
        h="100%",
    )


def home():
    """The home page."""
    return container(
        pc.grid(
            tabs(),
            feed(HomeState),
            sidebar(HomeState),
            grid_template_columns="1fr 2fr 1fr",
            h="100vh",
            gap=4,
        ),
        max_width="1300px",
    )
