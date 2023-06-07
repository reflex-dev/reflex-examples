"""A Pynecone example of a analog clock."""

import asyncio
from datetime import datetime
from typing import Any

import pynecone as pc
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


class State(pc.State):
    """The app state."""

    # The time zone to display the clock in.
    zone: str = "US/Pacific"

    # Whether the clock is running.
    running: bool = False

    @pc.var
    def time_info(self) -> dict[str, Any]:
        """Get the current time info.

        This can also be done as several computed vars, but this is more concise.

        Returns:
            A dictionary of the current time info.
        """
        now = datetime.now(pytz.timezone(self.zone))
        return {
            "hour": now.hour % 12,
            "minute": now.minute,
            "second": now.second,
            "meridiem": "AM" if now.hour < 12 else "PM",
            "minute_display": f"{now.minute:02}",
            "second_display": f"{now.second:02}",
            "hour_rotation": rotate(now.hour * 30 - 90),
            "minute_rotation": rotate(now.minute * 0.0167 * 360 - 90),
            "second_rotation": rotate(now.second * 0.0167 * 360 - 90),
        }

    async def tick(self):
        """Update the clock every second."""
        # Sleep for a second.
        await asyncio.sleep(1)

        # If the clock is running, tick again.
        if self.running:
            return self.tick

    def flip_switch(self, running: bool):
        """Start or stop the clock.

        Args:
            running: Whether the clock should be running.
        """
        # Set the switch state.
        self.running = running

        # Start the clock if the switch is on.
        if self.running:
            return self.tick


def clock_hand(rotation: str, color: str, length: str) -> pc.Component:
    """Create a clock hand.

    Args:
        rotation: The rotation of the clock hand.
        color: The color of the clock hand.
        length: The length of the clock hand.

    Returns:
        A clock hand component.
    """
    return pc.divider(
        transform=rotation,
        width=f"{length}em",
        position="absolute",
        border_style="solid",
        border_width="4px",
        border_image=f"linear-gradient(to right, rgb(250,250,250) 50%, {color} 100%) 0 0 100% 0",
        z_index=0,
    )


def analog_clock() -> pc.Component:
    """Create the analog clock."""
    return pc.circle(
        # The inner circle.
        pc.circle(
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


def digital_clock() -> pc.Component:
    """Create the digital clock."""
    return pc.hstack(
        pc.heading(State.time_info["hour"]),
        pc.heading(":"),
        pc.heading(State.time_info["minute_display"]),
        pc.heading(":"),
        pc.heading(State.time_info["second_display"]),
        pc.heading(State.time_info["meridiem"]),
        border_width="medium",
        border_color="#43464B",
        border_radius="2em",
        padding_x="2em",
        bg="white",
        color="#333",
    )


def timezone_select() -> pc.Component:
    """Create the timezone select."""
    return pc.select(
        TIMEZONES,
        placeholder="Select a time zone.",
        on_change=State.set_zone,
        bg="#white",
    )


def index():
    """The main view."""
    return pc.center(
        pc.vstack(
            analog_clock(),
            pc.hstack(
                digital_clock(),
                pc.switch(is_checked=State.running, on_change=State.flip_switch),
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
app = pc.App(state=State)
app.add_page(index, title="Clock")
app.compile()
