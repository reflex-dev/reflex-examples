"""A Pynecone example of a analog clock."""
import pynecone as pc
from datetime import datetime
import pytz
import asyncio


class State(pc.State):
    zone: str = "US/Pacific"
    start: bool = False
    _now: datetime = datetime.now(pytz.timezone(zone=zone))

    @pc.var
    def hour(self):
        return self._now.hour % 12

    @pc.var
    def minute(self):
        return self._now.minute

    @pc.var
    def minute_display(self):
        return f"{self.minute:02}"

    @pc.var
    def second(self):
        return self._now.second

    @pc.var
    def second_display(self):
        return f"{self.second:02}"

    @pc.var
    def meridiem(self):
        if self._now.hour < 12:
            return "AM"
        else:
            return "PM"

    @pc.var
    def minute_rotation(self):
        minute = self.minute * 0.0167 * 360 - 90
        return f"rotate({minute}deg)"

    @pc.var
    def hour_rotation(self):
        hour = self.hour * 30 - 90
        return f"rotate({hour}deg)"

    @pc.var
    def second_rotation(self):
        second = self.second * 0.0167 * 360 - 90
        return f"rotate({second}deg)"

    async def tick(self):
        """Update the clock every second."""
        self._now = datetime.now(pytz.timezone(self.zone))
        if self.start:
            await asyncio.sleep(1)
            return self.tick

    def flip_switch(self, start):
        """Start or stop the clock."""
        self.start = start
        if self.start:
            return self.tick


def current_hour(hour):
    """The hour hand."""
    return pc.divider(
        transform=hour,
        width="20em",
        position="absolute",
        border_style="solid",
        border_width="4px",
        border_image="linear-gradient(to right, rgb(250,250,250) 50%, black 100%) 0 0 100% 0",
        z_index=0,
    )


def current_minute(minute):
    """The minute hand."""
    return pc.divider(
        transform=minute,
        width="18em",
        position="absolute",
        border_style="solid",
        border_width="4px",
        border_image="linear-gradient(to right, rgb(250,250,250) 50%, red 100%) 0 0 100% 0",
        z_index=0,
    )


def current_second(second):
    """The second hand."""
    return pc.divider(
        transform=second,
        width="16em",
        position="absolute",
        border_style="solid",
        border_width="4px",
        border_image="linear-gradient(to right, rgb(250,250,250) 50%, blue 100%) 0 0 100% 0",
        z_index=0,
    )


def index():
    """The main view."""
    return pc.center(
        pc.vstack(
            pc.circle(
                pc.circle(
                    width="1em",
                    height="1em",
                    border_width="thick",
                    border_color="#43464B",
                    z_index=1,
                ),
                current_minute(State.minute_rotation),
                current_hour(State.hour_rotation),
                current_second(State.second_rotation),
                border_width="thick",
                border_color="#43464B",
                width="25em",
                height="25em",
                bg="rgb(250,250,250)",
                box_shadow="dark-lg",
            ),
            pc.hstack(
                pc.hstack(
                    pc.heading(State.hour),
                    pc.heading(":"),
                    pc.heading(State.minute_display),
                    pc.heading(":"),
                    pc.heading(State.second_display),
                    pc.heading(State.meridiem),
                    border_width="medium",
                    border_color="#43464B",
                    border_radius="2em",
                    padding_x="2em",
                    bg="white",
                    color="#333",
                ),
                pc.switch(is_checked=State.start, on_change=State.flip_switch),
            ),
            pc.select(
                [
                    "Asia/Tokyo",
                    "Australia/Sydney",
                    "Europe/London",
                    "Europe/Paris",
                    "Europe/Moscow",
                    "US/Pacific",
                    "US/Eastern",
                ],
                placeholder="Select a time zone.",
                on_change=State.set_zone,
                bg="#white",
            ),
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
