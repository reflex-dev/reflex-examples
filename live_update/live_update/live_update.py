"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import asyncio
from typing import Any
import httpx

import reflex as rx
from datetime import datetime
from lorem_text import lorem
import random


# class UpdateRow(rx.Base):
#     timestamp: datetime = datetime.now()
#     text: str = ""
#     id: int

#     def dict(self, *args, **kwargs) -> dict:
#         d = super().dict(*args, **kwargs)
#         d["timestamp"] = self.timestamp.replace(microsecond=0).isoformat()
#         return d


class State(rx.State):
    """The app state."""

    # data: list[UpdateRow]
    paused: bool
    chart_data: list[dict[str, int]] = [
        {"v1": 1},
        {"v1": 2},
        {"v1": 3},
        {"v1": 1},
        {"v1": 2},
        {"v1": 2},
        {"v1": 1},
        {"v1": 3},
        {"v1": 4},
        {"v1": 5},
    ]
    rate: int = 1

    # @rx.background
    # async def live_update(self):
    #     yield State.live_stream

    #     count = 0
    #     await asyncio.sleep(2)
    #     while True:
    #         await asyncio.sleep(1)
    #         if self.paused:
    #             continue

    #         row = UpdateRow(text=lorem.sentence(), id=count)
    #         count += 1

    #         async with self:
    #             if len(self.data) >= 5:
    #                 self.data.pop(0)
    #             self.data.append(row)

    @rx.background
    async def live_stream(self):
        while True:
            await asyncio.sleep(1 / self.rate)
            if self.paused:
                continue

            async with self:
                if len(self.chart_data) > 500:
                    self.chart_data.pop(0)
                # res = httpx.get("myapiurl.com/....")
                # res.json()
                val = random.randint(-4, 4)
                self.chart_data.append({"v1": 5 + val})

    def toggle_pause(self):
        self.paused = not self.paused

    def clear_data(self):
        self.data = []


def render_chart():
    return rx.recharts.line_chart(
        rx.recharts.line(data_key="v1", stroke="red", fill="red"),
        rx.recharts.x_axis(),
        rx.recharts.y_axis(),
        data=State.chart_data,
    )


def render_row(row):
    return rx.cond(
        row.id % 2,
        rx.hstack(
            rx.spacer(),
            rx.text(row.text, width="30vw", class_name="red-400"),
            rx.text(row.timestamp),
            width="60vw",
            class_name="bg-gray-200",
        ),
        rx.hstack(
            rx.text(row.text, width="30vw"),
            rx.spacer(),
            rx.text(row.timestamp),
            width="60vw",
            class_name="bg-gray-300",
        ),
    )


def rate_button(rate):
    return rx.button(
        rate,
        on_click=lambda: State.set_rate(rate),
    )


def render_rate_buttons():
    return rx.hstack(
        rx.button_group(
            rate_button(1),
            rate_button(10),
            rate_button(100),
            rate_button(1000),
            rate_button(10000),
            is_attached=True,
        ),
        rx.text(State.rate, " update per sec"),
        pause_button(),
    )


def pause_button():
    return rx.cond(
        ~State.paused,
        rx.button("Pause", on_click=State.toggle_pause),
        rx.button("Resume", on_click=State.toggle_pause),
    )


def clear_button():
    return rx.button("Clear", on_click=State.clear_data)


def render_text_update():
    return rx.vstack(
        rx.hstack(
            rx.heading(
                "Test live update",
                class_name="text-red-500",
            ),
            rx.spacer(),
            pause_button(),
            clear_button(),
            class_name="bg-gray-500 border border-black",
            width="100%",
        ),
        rx.foreach(State.data, lambda row: render_row(row)),
        class_name="border-gray-500",
        spacing="0",
        width="60vw",
    )


@rx.page(route="/", on_load=State.live_stream)
def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            render_rate_buttons(),
            render_chart(),
            rx.data_editor(
                columns=[{"title": "V1", "id": "v1", "type": "int"}],
                data=State.chart_data,
                rows=500,
                height="60vh",
            ),
            width="60vw",
        )
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.compile()
