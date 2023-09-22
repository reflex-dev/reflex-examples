"""A Reflex example of a analog clock."""

import asyncio
from datetime import datetime, timezone
from typing import Any

import reflex as rx
import pytz


# The supported time zones.
TIMEZONES = [
    "Asia/Tokyo",
    "Australia/Sydney",
    "Europe/London",
    "Europe/Paris",
    "Europe/Moscow",
    "US/Pacific",
    "US/Eastern",
]


def rotate(degrees: int) -> str:
    """CSS to rotate a clock hand.

    Args:
        degrees: The degrees to rotate the clock hand.

    Returns:
        The CSS to rotate the clock hand.
    """
    return f"rotate({degrees}deg)"


class State(rx.State):
    """The app state."""

    # The time zone to display the clock in.
    zone: str = rx.Cookie("US/Pacific")

    # Whether the clock is running.
    running: bool = False

    # The last updated timestamp
    _now: datetime = datetime.now(timezone.utc)

    @rx.cached_var
    def time_info(self) -> dict[str, Any]:
        """Get the current time info.

        This can also be done as several computed vars, but this is more concise.

        Returns:
            A dictionary of the current time info.
        """
        now = self._now.astimezone(pytz.timezone(self.zone))
        return {
            "hour": now.hour if now.hour <= 12 else now.hour % 12,
            "minute": now.minute,
            "second": now.second,
            "meridiem": "AM" if now.hour < 12 else "PM",
            "minute_display": f"{now.minute:02}",
            "second_display": f"{now.second:02}",
            "hour_rotation": rotate(now.hour * 30 - 90),
            "minute_rotation": rotate(now.minute * 0.0167 * 360 - 90),
            "second_rotation": rotate(now.second * 0.0167 * 360 - 90),
        }

    def on_load(self):
        """Switch the clock off when the page refreshes."""
        self.running = False
        self.refresh()

    def refresh(self):
        """Refresh the clock."""
        self._now = datetime.now(timezone.utc)

    @rx.background
    async def tick(self):
        """Update the clock every second."""
        while self.running:
            async with self:
                self.refresh()

            # Sleep for a second.
            await asyncio.sleep(1)

    def flip_switch(self, running: bool):
        """Start or stop the clock.

        Args:
            running: Whether the clock should be running.
        """
        # Set the switch state.
        self.running = running

        # Start the clock if the switch is on.
        if self.running:
            return State.tick


def clock_hand(rotation: str, color: str, length: str) -> rx.Component:
    """Create a clock hand.

    Args:
        rotation: The rotation of the clock hand.
        color: The color of the clock hand.
        length: The length of the clock hand.

    Returns:
        A clock hand component.
    """
    return rx.divider(
        transform=rotation,
        width=f"{length}em",
        position="absolute",
        border_style="solid",
        border_width="4px",
        border_image=f"linear-gradient(to right, rgb(250,250,250) 50%, {color} 100%) 0 0 100% 0",
        z_index=0,
    )


def analog_clock() -> rx.Component:
    """Create the analog clock."""
    return rx.circle(
        # The inner circle.
        rx.circle(
            width="1em",
            height="1em",
            border_width="thick",
            border_color="#43464B",
            z_index=1,
        ),
        # The clock hands.
        clock_hand(State.time_info["hour_rotation"], "black", "16"),
        clock_hand(State.time_info["minute_rotation"], "red", "18"),
        clock_hand(State.time_info["second_rotation"], "blue", "19"),
        border_width="thick",
        border_color="#43464B",
        width="25em",
        height="25em",
        bg="rgb(250,250,250)",
        box_shadow="dark-lg",
    )


def digital_clock() -> rx.Component:
    """Create the digital clock."""
    return rx.hstack(
        rx.heading(State.time_info["hour"]),
        rx.heading(":"),
        rx.heading(State.time_info["minute_display"]),
        rx.heading(":"),
        rx.heading(State.time_info["second_display"]),
        rx.heading(State.time_info["meridiem"]),
        border_width="medium",
        border_color="#43464B",
        border_radius="2em",
        padding_x="2em",
        bg="white",
        color="#333",
    )


def timezone_select() -> rx.Component:
    """Create the timezone select."""
    return rx.select(
        TIMEZONES,
        placeholder="Select a time zone.",
        on_change=State.set_zone,
        value=State.zone,
        bg="#white",
    )


def index():
    """The main view."""
    return rx.center(
        rx.vstack(
            analog_clock(),
            rx.hstack(
                digital_clock(),
                rx.switch(is_checked=State.running, on_change=State.flip_switch),
            ),
            timezone_select(),
            padding="5em",
            border_width="medium",
            border_color="#43464B",
            border_radius="25px",
            bg="#ededed",
            text_align="center",
        ),
        padding="5em",
    )


# Add state and page to the app.
app = rx.App(state=State)
app.add_page(index, title="Clock", on_load=State.on_load)
app.compile()
