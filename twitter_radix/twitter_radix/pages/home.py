"""The home page. This file includes examples abstracting complex UI into smaller components."""
import reflex as rx
import reflex.components.radix.themes as rdxt
from twitter_radix.state.base import State
from twitter_radix.state.home import HomeState

from ..components import container


def tab_button(name, href):
    """A tab switcher button."""
    return rdxt.link(
        rdxt.flex(rdxt.icon(tag="star"), mr="2"),
        name,
        display="inline-flex",
        align_items="center",
        padding="0.75rem",
        href=href,
        border="1px solid #eaeaea",
        font_weight="semibold",
        border_radius="2rem",
    )


def tabs():
    """The tab switcher displayed on the left."""
    return rdxt.box(
        rx.vstack(
            rdxt.heading("PySocial", size="5"),
            tab_button("Home", "/"),
            rdxt.box(
                rdxt.heading("Followers", size="3"),
                rx.foreach(
                    HomeState.followers,
                    lambda follow: rx.vstack(
                        rx.hstack(
                            rdxt.avatar(fallback=follow.follower_username, size="3"),
                            rdxt.text(follow.follower_username),
                        ),
                        padding="1em",
                    ),
                ),
                p="4",
                border_radius="0.5rem",
                border="1px solid #eaeaea",
            ),
            rdxt.button("Sign out", on_click=State.logout, size="3"),
            align_items="left",
            gap=4,
        ),
        py="4",
    )


def sidebar(HomeState):
    """The sidebar displayed on the right."""
    return rx.vstack(
        rx.input(
            on_change=HomeState.set_friend,
            placeholder="Search users",
            width="100%",
        ),
        rx.foreach(
            HomeState.search_users,
            lambda user: rx.vstack(
                rx.hstack(
                    rdxt.avatar(fallback=user.username, size="3"),
                    rdxt.text(user.username),
                    rx.spacer(),
                    rdxt.button(
                        rdxt.icon(tag="plus"),
                        on_click=lambda: HomeState.follow_user(user.username),
                    ),
                    width="100%",
                ),
                py=2,
                width="100%",
            ),
        ),
        rdxt.box(
            rdxt.heading("Following", size="3"),
            rx.foreach(
                HomeState.following,
                lambda follow: rx.vstack(
                    rx.hstack(
                        rdxt.avatar(fallback=follow.followed_username, size="3"),
                        rdxt.text(follow.followed_username),
                    ),
                    padding="1em",
                ),
            ),
            p="4",
            border_radius="0.5rem",
            border="1px solid #eaeaea",
            width="100%",
        ),
        align_items="start",
        gap=4,
        h="100%",
        py=4,
    )


def feed_header(HomeState):
    """The header of the feed."""
    return rx.hstack(
        rdxt.heading("Home", size="5"),
        rx.input(on_change=HomeState.set_search, placeholder="Search tweets"),
        justify="space-between",
        p=4,
        border_bottom="1px solid #ededed",
    )


def composer(HomeState):
    """The composer for new tweets."""
    return rx.grid(
        rx.vstack(
            rdxt.avatar(fallback=State.user.username.to_string(), size="4"),
            p=4,
        ),
        rdxt.box(
            rdxt.flex(
                rdxt.textarea(
                    width="100%",
                    #border="none",
                    #padding_y="2rem",
                    placeholder="What's happening?",
                    resize="none",
                    _focus={"border": 0, "outline": 0, "boxShadow": "none"},
                    on_blur=HomeState.set_tweet,
                ),
                py="4",
            ),
            
            rx.hstack(
                rdxt.button(
                    "Tweet",
                    on_click=HomeState.post_tweet,
                    color="white",
                    radius="full",
                    size="3",
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
    return rx.grid(
        rx.vstack(
            rdxt.avatar(fallback=tweet.author, size="3"),
        ),
        rdxt.box(
            rx.vstack(
                rdxt.text("@" + tweet.author, font_weight="bold"),
                rdxt.text(tweet.content, width="100%"),
                align_items="left",
            ),
        ),
        grid_template_columns="1fr 5fr",
        py=4,
        gap=1,
        border_bottom="1px solid #ededed",
    )


def feed(HomeState):
    """The feed."""
    return rdxt.box(
        feed_header(HomeState),
        composer(HomeState),
        rx.cond(
            HomeState.tweets,
            rx.foreach(
                HomeState.tweets,
                tweet,
            ),
            rx.vstack(
                rdxt.button(
                    rdxt.icon(
                        tag="update",
                    ),
                    rdxt.text("Click to load tweets"),
                    on_click=HomeState.get_tweets,
                ),
                p=4,
            ),
        ),
        border_left="1px solid #ededed",
        border_right="1px solid #ededed",
        height="100%",
    )


def home():
    """The home page."""
    return container(
        rx.grid(
            tabs(),
            feed(HomeState),
            sidebar(HomeState),
            grid_template_columns="1fr 2fr 1fr",
            h="100vh",
            gap=4,
        ),
        max_width="1300px",
    )
