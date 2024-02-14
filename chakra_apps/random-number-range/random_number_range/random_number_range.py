"""This example demonstrates two techniques for achieving a long running task:

Chained Events: each step of the event recursively queues itself to run again.
Background Tasks: a background task is started and runs until it is cancelled.

The background task is the newer approach and is generally preferrable because
it does not block UI interaction while it is running.
"""
import asyncio
import random
from typing import List

import reflex as rx


class BaseState(rx.State):
    rrange: List[int] = [-10, 10]
    delay: int = 1
    _last_values: List[int] = []
    total: int = 0

    @rx.var
    def last_values(self) -> str:
        return ", ".join(str(x) for x in self._last_values[-10:])

    def balance(self):
        max_magnitude = max(abs(x) for x in self.rrange)
        self.rrange = [-max_magnitude, max_magnitude]


class BackgroundState(BaseState):
    running: bool = False
    loading: bool = False
    _n_tasks: int = 0

    @rx.background
    async def run_task(self):
        async with self:
            if self._n_tasks > 0:
                return
            self._n_tasks += 1

        while True:
            async with self:
                self.loading = True

            # Simulate long running API call
            await asyncio.sleep(self.delay)

            async with self:
                last_value = random.randint(*self.rrange)
                self.total += last_value
                self._last_values = self._last_values[-9:] + [last_value]
                self.loading = False
                if not self.running:
                    break

        async with self:
            self._n_tasks -= 1

    def set_running(self, value: bool):
        self.running = value
        if value:
            return BackgroundState.run_task

    def single_step(self):
        self.running = False
        return BackgroundState.run_task


class ChainState(BaseState):
    running: bool = False
    loading: bool = False

    async def run_task(self):
        self.loading = True
        yield

        # Simulate long running API call
        await asyncio.sleep(self.delay)

        last_value = random.randint(*self.rrange)
        self.total += last_value
        self._last_values = self._last_values[-9:] + [last_value]
        self.loading = False

        if self.running:
            yield ChainState.run_task

    def set_running(self, value: bool):
        self.running = value
        if self.running:
            return ChainState.run_task

    def single_step(self):
        self.running = False
        return ChainState.run_task


other_links = {
    "Chain Events": lambda State: rx.chakra.link("Background Task Version", href="/background", on_click=State.set_running(False)),
    "Background Task": lambda State: rx.chakra.link("Chain Event Version", href="/chain", on_click=State.set_running(False)),
}


def random_numbers_in_range(State, mode: str) -> rx.Component:
    return rx.chakra.center(
        rx.chakra.vstack(
            rx.chakra.heading(f"Random Numbers in Range"),
            rx.chakra.heading(f"{mode} version", font_size="1.5em"),
            other_links[mode](State),
            rx.chakra.hstack(
                rx.chakra.text("Min: ", State.rrange[0], padding_right="3em"),
                rx.chakra.button("Balance", on_click=State.balance),
                rx.chakra.text("Max: ", State.rrange[1], padding_left="3em"),
            ),
            rx.chakra.range_slider(value=State.rrange, on_change=State.set_rrange, min_=-100, max_=100),
            rx.chakra.hstack(
                rx.chakra.text("Last 10 values: ", State.last_values),
                rx.cond(State.loading, rx.chakra.spinner()),
            ),
            rx.chakra.hstack(
                rx.chakra.text("Total: ", State.total),
                rx.chakra.button("Clear", on_click=lambda: State.set_total(0)),
            ),
            rx.chakra.hstack(
                rx.chakra.vstack(
                    rx.chakra.text("Run", font_size="0.7em"),
                    rx.chakra.switch(is_checked=State.running, on_change=State.set_running),
                ),
                rx.chakra.vstack(
                    rx.chakra.text("Delay (sec)", font_size="0.7em"),
                    rx.chakra.select(*[rx.chakra.option(x) for x in range(1, 5)], value=State.delay.to(str), on_change=State.set_delay),
                    padding_right="3em",
                ),
                rx.chakra.button("Single Step", on_click=State.single_step),
                align_items="flex-start",
            ),
            width="50vw",
        ),
    )


app = rx.App()
app.add_page(rx.fragment(on_mount=rx.redirect("/chain")), route="/")
app.add_page(random_numbers_in_range(ChainState, "Chain Events"), route="/chain")
app.add_page(random_numbers_in_range(BackgroundState, "Background Task"), route="/background")
