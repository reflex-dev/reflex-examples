import asyncio
import random

import reflex as rx
from lorem_text import lorem

ITERATIONS_RANGE = (7, 12)


class LoremState(rx.State):
    running: dict[int, bool] = {}
    progress: dict[int, int] = {}
    end_at: dict[int, int] = {}
    text: dict[int, str] = {}

    _next_task_id: int = 0

    @rx.var(cache=True)
    def task_ids(self) -> list[int]:
        return list(reversed(self.text))

    @rx.event(background=True)
    async def stream_text(self, task_id: int = -1):
        if task_id < 0:
            async with self:
                task_id = self._next_task_id
                self._next_task_id += 1
                self.end_at[task_id] = random.randint(*ITERATIONS_RANGE)

        async with self:
            self.running[task_id] = True
            start = self.progress.get(task_id, 0)

        for progress in range(start, self.end_at.get(task_id, 0)):
            await asyncio.sleep(0.5)
            async with self:
                if not self.running.get(task_id):
                    return
                self.text[task_id] = self.text.get(task_id, "") + lorem.words(3) + " "
                self.progress[task_id] = progress + 1

        async with self:
            self.running.pop(task_id, None)

    @rx.event
    def toggle_running(self, task_id: int):
        if self.progress.get(task_id, 0) >= self.end_at.get(task_id, 0):
            self.progress[task_id] = 0
            self.end_at[task_id] = random.randint(*ITERATIONS_RANGE)
            self.text[task_id] = ""
        if self.running.get(task_id):
            self.running[task_id] = False
        else:
            return LoremState.stream_text(task_id)

    @rx.event
    def kill(self, task_id: int):
        self.running.pop(task_id, None)
        self.text.pop(task_id, None)


def render_task(task_id: int) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.badge("Task ", task_id),
            rx.button(
                rx.cond(
                    LoremState.progress[task_id] < LoremState.end_at[task_id], "⏯️", "🔄"
                ),
                on_click=LoremState.toggle_running(task_id),
                variant="outline",
            ),
            rx.button(
                "❌",
                on_click=LoremState.kill(task_id),
                variant="outline",
            ),
        ),
        rx.progress(
            value=LoremState.progress[task_id],
            max=LoremState.end_at[task_id],
            min_height="10px",
            max_height="10px",
        ),
        rx.text(LoremState.text[task_id], overflow_y="scroll"),
        rx.spacer(),
        width=["180px", "190px", "210px", "240px", "300px"],
        height="300px",
        padding="10px",
    )


def example() -> rx.Component:
    return rx.vstack(
        rx.button(
            "➕ New Task",  # noqa: RUF001
            on_click=LoremState.stream_text(-1),
            variant="surface",
        ),
        rx.flex(
            rx.foreach(LoremState.task_ids, render_task),
            flex_wrap="wrap",
            width="100%",
        ),
        align="center",
        padding_top="20px",
    )
