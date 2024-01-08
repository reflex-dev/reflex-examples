from rxconfig import config

import reflex as rx
import random
import asyncio
from collections import deque

GRID_SIZE = 7


def generate_graph(walls, size) -> list[list[int]]:
    """Generate a 2D grid of size x size with walls number of walls."""
    color = [0] * (size**2)

    while walls > 0:
        wall = random.randint(size, size**2 - 1)
        if color[wall] != "blue":
            color[wall] = "blue"
            walls -= 1

    color[random.randint(0, size - 1)] = "red"
    color[random.randint(size, size**2 - 1)] = "green"

    def to_matrix(l, n):
        return [l[i : i + n] for i in range(0, len(l), n)]

    return to_matrix(color, GRID_SIZE)


class State(rx.State):
    """The app state."""

    option: str = ""
    walls: int = 0
    colored_graph: list[list[int]] = generate_graph(walls, GRID_SIZE)
    initial: bool = True
    s: list = []
    q: list = []

    def set_walls(self, value):
        if value != "":
            if int(value) >= 0:
                self.walls = int(value)

    def new_graph(self):
        """Reset the state with parameters."""
        self.colored_graph = generate_graph(self.walls, GRID_SIZE)
        self.initial = True
        self.s = []
        self.q = []

    def run(self):
        """Run the selected algorithm."""
        if self.option == "DFS":
            return State.run_dfs
        elif self.option == "BFS":
            return State.run_bfs

    async def run_dfs(self):
        """DFS algorithm on a 1d array."""
        await asyncio.sleep(0.01)
        colors = self.colored_graph

        if self.initial:
            for i in range(len(colors)):
                for j in range(len(colors[i])):
                    if colors[i][j] == "red":
                        self.s.append((i, j))
                        self.initial = False
                        break

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        if self.s:
            i, j = self.s.pop()

            if colors[i][j] == "green":
                self.colored_graph = colors
                return

            if colors[i][j] != "red":
                colors[i][j] = "yellow"

            self.colored_graph = colors

            for di, dj in directions:
                i2, j2 = i + di, j + dj
                if (
                    0 <= i2 < len(colors)
                    and 0 <= j2 < len(colors[i2])
                    and colors[i2][j2] != "yellow"
                    and colors[i2][j2] != "blue"
                ):
                    self.s.append((i2, j2))
            return State.run_dfs

        return rx.window_alert("No path found")

    async def run_bfs(self):
        await asyncio.sleep(0.000000000000000001)
        colors = self.colored_graph
        q = deque()

        if self.q != []:
            for item in self.q:
                q.append(item)

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        if self.initial:
            for i in range(len(colors)):
                for j in range(len(colors[i])):
                    if colors[i][j] == "red":
                        q.append((i, j))
                        self.q.append((i, j))
                        self.initial = False
                        break

        if q:
            i, j = q.popleft()
            self.q.pop(0)

            if colors[i][j] == "green":
                self.colored_graph = colors
                return

            if colors[i][j] != "red":
                colors[i][j] = "yellow"

            self.colored_graph = colors

            for di, dj in directions:
                i2, j2 = i + di, j + dj
                if (
                    0 <= i2 < len(colors)
                    and 0 <= j2 < len(colors[i2])
                    and colors[i2][j2] != "yellow"
                    and colors[i2][j2] != "blue"
                ):
                    q.append((i2, j2))
                    self.q.append((i2, j2))
            return State.run_bfs

        return rx.window_alert("No path found")


def render_box(color):
    """Return a colored box."""
    return rx.box(bg=color, width="50px", height="50px", border="1px solid black")


def index():
    return rx.center(
        rx.vstack(
            rx.heading("Graph Traversal", font_size="2.8em"),
            rx.hstack(
                rx.number_input(
                    on_change=State.set_walls,
                    bg="white",
                    min_=0,
                    max_=20,
                    is_invalid=False,
                    default_value=0,
                ),
                rx.button(
                    "Generate Graph",
                    on_click=State.new_graph,
                    width="100%",
                    bg="white",
                ),
            ),
            rx.responsive_grid(
                rx.foreach(
                    State.colored_graph, lambda x: rx.vstack(rx.foreach(x, render_box))
                ),
                columns=[GRID_SIZE],
                spacing="2",
                justify="center",
            ),
            rx.hstack(
                rx.select(
                    ["DFS", "BFS"],
                    placeholder="Select an algorithm..",
                    on_change=State.set_option,
                    width="100%",
                    bg="white",
                ),
                rx.button(
                    "run",
                    on_click=State.run,
                    width="50%",
                    bg="white",
                ),
                width="100%",
            ),
            bg="#cdcdcd",
            padding="2em",
        ),
    )


app = rx.App()
app.add_page(index)
