"""The dashboard page for the template."""
import reflex as rx
import asyncio
import random
import httpx

from ..state import State
from ..states.pie_state import PieChartState
from demo.styles import *


data_1 = [
    {"name": "Page A", "uv": 4000, "pv": 2400, "amt": 2400},
    {"name": "Page B", "uv": 3000, "pv": 1398, "amt": 2210},
    {"name": "Page C", "uv": 2000, "pv": 9800, "amt": 2290},
    {"name": "Page D", "uv": 2780, "pv": 3908, "amt": 2000},
    {"name": "Page E", "uv": 1890, "pv": 4800, "amt": 2181},
    {"name": "Page F", "uv": 2390, "pv": 3800, "amt": 2500},
    {"name": "Page G", "uv": 3490, "pv": 4300, "amt": 2100},
]
data_1_show = """data = [
    {"name": "Page A", "uv": 4000, "pv": 2400, "amt": 2400},
    {"name": "Page B", "uv": 3000, "pv": 1398, "amt": 2210},
    {"name": "Page C", "uv": 2000, "pv": 9800, "amt": 2290},
    {"name": "Page D", "uv": 2780, "pv": 3908, "amt": 2000},
    {"name": "Page E", "uv": 1890, "pv": 4800, "amt": 2181},
    {"name": "Page F", "uv": 2390, "pv": 3800, "amt": 2500},
    {"name": "Page G", "uv": 3490, "pv": 4300, "amt": 2100},
]"""


graph_1_code = """rx.recharts.composed_chart(
    rx.recharts.area(
        data_key="uv", stroke="#8884d8", fill="#8884d8"
    ),
    rx.recharts.bar(
        data_key="amt", bar_size=20, fill="#413ea0"
    ),
    rx.recharts.line(
        data_key="pv", type_="monotone", stroke="#ff7300"
    ),
    rx.recharts.x_axis(data_key="name"),
    rx.recharts.y_axis(),
    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
    rx.recharts.graphing_tooltip(),
    data=data,
)"""


graph_2_code = """rx.recharts.pie_chart(
    rx.recharts.pie(
        data=PieChartState.resources,
        data_key="count",
        name_key="type_",
        cx="50%",
        cy="50%",
        fill="#8884d8",
        label=True,
    ),
    rx.recharts.graphing_tooltip(),
),
rx.vstack(
    rx.foreach(
        PieChartState.resource_types,
        lambda type_, i: rx.hstack(
            rx.button(
                "-",
                on_click=PieChartState.decrement(type_),
            ),
            rx.text(
                type_,
                PieChartState.resources[i]["count"],
            ),
            rx.button(
                "+",
                on_click=PieChartState.increment(type_),
            ),
        ),
    ),
)"""

graph_2_state = """class PieChartState(rx.State):
    resources: list[dict[str, Any]] = [
        dict(type_="🏆", count=1),
        dict(type_="🪵", count=1),
        dict(type_="🥑", count=1),
        dict(type_="🧱", count=1),
    ]

    @rx.cached_var
    def resource_types(self) -> list[str]:
        return [r["type_"] for r in self.resources]

    def increment(self, type_: str):
        for resource in self.resources:
            if resource["type_"] == type_:
                resource["count"] += 1
                break

    def decrement(self, type_: str):
        for resource in self.resources:
            if (
                resource["type_"] == type_
                and resource["count"] > 0
            ):
                resource["count"] -= 1
                break
"""


graph_3_code = """rx.stack(
    rx.cond(
        ~GraphLiveState.paused,
        rx.button("Pause", on_click=GraphLiveState.toggle_pause),
        rx.button("Resume", on_click=GraphLiveState.toggle_pause),
    ),
),
rx.recharts.line_chart(
    rx.recharts.line(data_key="v1", stroke="red", fill="red"),
    rx.recharts.x_axis(),
    rx.recharts.y_axis(domain=[5, 25]),
    data=GraphLiveState.chart_data,
)"""


graph_3_state = """class GraphLiveState(State):
    "The app state."

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
    rate: int = 10

    @rx.background
    async def live_stream(self):
        while True:
            await asyncio.sleep(1 / self.rate)
            if self.paused:
                continue

            async with self:
                if len(self.chart_data) > 500:
                    self.chart_data.pop(0)

                val = random.randint(-4, 4)
                self.chart_data.append({"v1": 5 + val})


                # If you want to call an API below is an example of how to do so for bitcoin prices
                # res = httpx.get("https://api.gemini.com/v2/ticker/btcusd")
                # data = res.json()
                # self.chart_data.append({"v1": data["ask"]})


    def toggle_pause(self):
        self.paused = not self.paused"""



class GraphLiveState(State):
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
    rate: int = 10

    @rx.background
    async def live_stream(self):
        while True:
            await asyncio.sleep(1 / self.rate)

            async with self:
                if self.paused:
                    continue

                if len(self.chart_data) > 500:
                    self.chart_data.pop(0)

                val = random.randint(-4, 4)
                self.chart_data.append({"v1": 5 + val})


                # If you want to call an API below is an example of how to do so for bitcoin prices
                # res = httpx.get("https://api.gemini.com/v2/ticker/btcusd")
                # data = res.json()
                # self.chart_data.append({"v1": data["ask"]})


    def toggle_pause(self):
        self.paused = not self.paused


def render_chart():
    return rx.recharts.line_chart(
        rx.recharts.line(data_key="v1", stroke="red", fill="red"),
        rx.recharts.x_axis(),
        rx.recharts.y_axis(domain=[5, 25]),
        data=GraphLiveState.chart_data,
    )


def pause_button():
    return rx.cond(
        ~GraphLiveState.paused,
        rx.button("Pause", on_click=GraphLiveState.toggle_pause),
        rx.button("Resume", on_click=GraphLiveState.toggle_pause),
    )





def graphing_page() -> rx.Component:
    """The UI for the dashboard page.

    Returns:
        rx.Component: The UI for the dashboard page.
    """
    return rx.box(
        rx.vstack(
            rx.heading(
                "Graphing Demo",
                font_size="3em",
            ),
            rx.heading(
                "Composed Chart",
                font_size="2em",
            ),
            rx.stack(
                rx.recharts.composed_chart(
                    rx.recharts.area(data_key="uv", stroke="#8884d8", fill="#8884d8"),
                    rx.recharts.bar(data_key="amt", bar_size=20, fill="#413ea0"),
                    rx.recharts.line(data_key="pv", type_="monotone", stroke="#ff7300"),
                    rx.recharts.x_axis(data_key="name"),
                    rx.recharts.y_axis(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    rx.recharts.graphing_tooltip(),
                    data=data_1,
                    # height="15em",
                ),
                width="100%",
                height="20em",
            ),
            rx.tabs(
                rx.tab_list(
                    rx.tab("Code", style=tab_style),
                    rx.tab("Data", style=tab_style),
                    padding_x=0,
                ),
                rx.tab_panels(
                    rx.tab_panel(
                        rx.code_block(
                            graph_1_code,
                            theme="light",
                            language="python",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            data_1_show,
                            theme="light",
                            language="python",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    width="100%",
                ),
                variant="unstyled",
                color_scheme="purple",
                align="end",
                width="100%",
                padding_top=".5em",
            ),
            rx.heading("Interactive Example", font_size="2em"),
            rx.hstack(
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        data=PieChartState.resources,
                        data_key="count",
                        name_key="type_",
                        cx="50%",
                        cy="50%",
                        fill="#8884d8",
                        label=True,
                    ),
                    rx.recharts.graphing_tooltip(),
                ),
                rx.vstack(
                    rx.foreach(
                        PieChartState.resource_types,
                        lambda type_, i: rx.hstack(
                            rx.button(
                                "-",
                                on_click=PieChartState.decrement(type_),
                            ),
                            rx.text(
                                type_,
                                PieChartState.resources[i]["count"],
                            ),
                            rx.button(
                                "+",
                                on_click=PieChartState.increment(type_),
                            ),
                        ),
                    ),
                ),
                width="100%",
                height="15em",
            ),
            rx.tabs(
                rx.tab_list(
                    rx.tab("Code", style=tab_style),
                    rx.tab("State", style=tab_style),
                    padding_x=0,
                ),
                rx.tab_panels(
                    rx.tab_panel(
                        rx.code_block(
                            graph_2_code,
                            theme="light",
                            language="python",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            graph_2_state,
                            theme="light",
                            language="python",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    width="100%",
                ),
                variant="unstyled",
                color_scheme="purple",
                align="end",
                width="100%",
                padding_top=".5em",
            ),
            rx.heading("Live Stream Data Example", font_size="2em"),
            rx.vstack(
                rx.stack(
                    pause_button(),
                ),
                render_chart(),
                width="100%",
                height="20em",
            ),
            rx.tabs(
                rx.tab_list(
                    rx.tab("Code", style=tab_style),
                    rx.tab("State", style=tab_style),
                    padding_x=0,
                ),
                rx.tab_panels(
                    rx.tab_panel(
                        rx.code_block(
                            graph_3_code,
                            theme="light",
                            language="python",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            graph_3_state,
                            theme="light",
                            language="python",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    width="100%",
                ),
                variant="unstyled",
                color_scheme="purple",
                align="end",
                width="100%",
                padding_top=".5em",
            ),
            style=template_content_style,
            min_h="100vh",
        ),
        style=template_page_style,
        min_h="100vh",
    )
