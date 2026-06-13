"""UI components for displaying tweets."""

import reflex as rx
from ..state.home import HomeState

def tweet_item(tweet) -> rx.Component:
    """Display a single tweet with edit/delete options."""
    return rx.box(
        rx.cond(
            HomeState.editing_tweet_id == tweet.id,
            # Edit mode
            rx.vstack(
                rx.hstack(
                    rx.avatar(name=tweet.author, size="3", color="#1DA1F2"),
                    rx.text(f"@{tweet.author}", font_weight="bold", color="#14171A"),
                    rx.spacer(),
                    width="100%",
                ),
                rx.text_area(
                    value=HomeState.edit_tweet_content,
                    on_change=HomeState.set_edit_tweet_content,
                    width="100%",
                    min_height="80px",
                    border_color="#E1E8ED",
                    _focus={"border_color": "#1DA1F2"},
                ),
                rx.hstack(
                    rx.button(
                        "Save",
                        on_click=lambda: HomeState.save_edit_tweet(tweet.id),
                        color="white",
                        bg="#1DA1F2",
                        _hover={"bg": "#1A91DA"},
                        border_radius="20px",
                        size="2",
                    ),
                    rx.button(
                        "Cancel",
                        on_click=HomeState.cancel_edit_tweet,
                        color="#14171A",
                        bg="white",
                        border="1px solid #E1E8ED",
                        _hover={"bg": "#F7F9FA"},
                        border_radius="20px",
                        size="2",
                    ),
                    spacing="2",
                ),
                spacing="3",
                width="100%",
            ),
            # View mode
            rx.vstack(
                rx.hstack(
                    rx.avatar(name=tweet.author, size="3", color="#1DA1F2"),
                    rx.vstack(
                        rx.text(f"@{tweet.author}", font_weight="bold", color="#14171A", size="3"),
                        rx.text(tweet.created_at, color="#657786", font_size="14px"),
                        spacing="0",
                        align_items="flex-start",
                    ),
                    rx.spacer(),
                    rx.cond(
                        tweet.author == HomeState.user.username,
                        rx.hstack(
                            rx.icon_button(
                                rx.icon("pencil", size=16),
                                on_click=lambda: HomeState.start_edit_tweet(tweet.id, tweet.content),
                                color="#657786",
                                variant="ghost",
                                _hover={"color": "#1DA1F2", "bg": "#F7F9FA"},
                                size="2",
                            ),
                            rx.icon_button(
                                rx.icon("trash-2", size=16),
                                on_click=lambda: HomeState.delete_tweet(tweet.id),
                                color="#657786",
                                variant="ghost",
                                _hover={"color": "#E0245E", "bg": "#F7F9FA"},
                                size="2",
                            ),
                            spacing="1",
                        ),
                    ),
                    width="100%",
                    align_items="flex-start",
                ),
                rx.text(tweet.content, color="#14171A", font_size="15px", width="100%"),
                spacing="2",
                width="100%",
                align_items="flex-start",
            ),
        ),
        padding="16px",
        border_bottom="1px solid #E1E8ED",
        _hover={"bg": "#F7F9FA"},
        width="100%",
    )