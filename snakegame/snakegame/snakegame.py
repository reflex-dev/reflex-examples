from typing import Any, Dict, List, Optional
import reflex as rx
import asyncio
import random

N = 19  # There is a N*N grid for ground of snake
COLOR_NONE = "#EEEEEE"
COLOR_BODY = "#008800"
COLOR_FOOD = "#FF00FF"
COLOR_DEAD = "#FF0000"
HEAD_U = "U"
HEAD_D = "D"
HEAD_L = "L"
HEAD_R = "R"


class State(rx.State):
    dir: str = HEAD_R  # direction of what head of snake face
    moves: list[str] = []
    snake: list[list[int]] = [
        [10, 10],
        [10, 11],
        [10, 12],
        [10, 13],
        [10, 14],
        [10, 15],
    ]  # all (X,Y) for snake's body
    food: list[int] = [5, 5]  # X, Y of food
    cells: list[str] = (N * N) * [COLOR_NONE]
    tick_cnt: int = 1
    score: int = 0
    magic: int = 1
    rate: int = 10
    running: bool = False
    died: bool = False
    _n_tasks: int = 0

    def turnOnTick(self):
        if not self.running:
            self.running = True
            return State.loop

    def turnOffTick(self):
        self.running = False

    def flip_switch(self, start):
        if self.running:
            return State.turnOffTick
        else:
            return State.turnOnTick

    @rx.background
    async def loop(self):
        async with self:
            if self._n_tasks > 0:
                return
            self._n_tasks += 1
            if self.died:
                self.died = False
                self.magic = 1
                for i in range(N * N):
                    self.cells[i] = COLOR_NONE
                self.snake = [
                    [10, 10],
                    [10, 11],
                    [10, 12],
                    [10, 13],
                    [10, 14],
                    [10, 15],
                ].copy()
                self.food = [5, 5]
                self.dir = HEAD_R
                self.moves = []

        while self.running:
            print(f"TICK: {self.tick_cnt}")
            await asyncio.sleep(0.5)
            async with self:
                head = self.snake[-1].copy()
                # XXX: hack needed until #1876 merges
                dir = self.moves[0] if self.moves else self.dir
                self.moves.pop(0) if self.moves else None
                self.dir = dir
                # XXX: end hack (should just use `.pop(0)`)
            print(head, dir)
            if dir == HEAD_U:
                head[1] += N - 1
                head[1] %= N
            elif dir == HEAD_D:
                head[1] += N + 1
                head[1] %= N
            elif dir == HEAD_L:
                head[0] += N - 1
                head[0] %= N
            elif dir == HEAD_R:
                head[0] += N + 1
                head[0] %= N
            async with self:
                if head in self.snake:
                    self.running = False
                    self.died = True
                    self.cells[head[0] + N * head[1]] = COLOR_DEAD
                    break

            # Move the snake
            async with self:
                self.cells[head[0] + N * head[1]] = COLOR_BODY
                self.snake.append(head.copy())
                FOOD_EATEN = False
                while self.food in self.snake:
                    FOOD_EATEN = True
                    self.food = [random.randint(0, N - 1), random.randint(0, N - 1)]
                self.cells[self.food[0] + N * self.food[1]] = COLOR_FOOD
                if FOOD_EATEN == False:
                    self.cells[self.snake[0][0] + N * self.snake[0][1]] = COLOR_NONE
                    del self.snake[0]
                else:
                    self.score += self.magic
                    self.magic += 1
                    self.rate = (int)(
                        100 * ((float)(self.score) / (float)(self.tick_cnt))
                    )
                self.tick_cnt += 1

        async with self:
            self._n_tasks -= 1

    def arrow_up(self):
        if (self.moves[-1] if self.moves else self.dir) != HEAD_D:
            self.moves.append(HEAD_U)

    def arrow_left(self):
        if (self.moves[-1] if self.moves else self.dir) != HEAD_R:
            self.moves.append(HEAD_L)

    def arrow_right(self):
        if (self.moves[-1] if self.moves else self.dir) != HEAD_L:
            self.moves.append(HEAD_R)

    def arrow_down(self):
        if (self.moves[-1] if self.moves else self.dir) != HEAD_U:
            self.moves.append(HEAD_D)

    def arrow_none(self):
        return

    def arrow_rel_left(self):
        last_dir = self.moves[-1] if self.moves else self.dir
        if last_dir == HEAD_U:
            self.arrow_left()
        elif last_dir == HEAD_L:
            self.arrow_down()
        elif last_dir == HEAD_D:
            self.arrow_right()
        elif last_dir == HEAD_R:
            self.arrow_up()

    def arrow_rel_right(self):
        last_dir = self.moves[-1] if self.moves else self.dir
        if last_dir == HEAD_U:
            self.arrow_right()
        elif last_dir == HEAD_L:
            self.arrow_up()
        elif last_dir == HEAD_D:
            self.arrow_left()
        elif last_dir == HEAD_R:
            self.arrow_down()

    def handle_key(self, key):
        if key == "ArrowUp":
            self.arrow_up()
        elif key == "ArrowLeft":
            self.arrow_left()
        elif key == "ArrowRight":
            self.arrow_right()
        elif key == "ArrowDown":
            self.arrow_down()
        elif key == ",":
            self.arrow_rel_left()
        elif key == ".":
            self.arrow_rel_right()
        else:
            print(key)


class GlobalKeyWatcher(rx.Fragment):
    # List of keys to trigger on
    keys: rx.vars.Var[List[str]] = []

    def _get_hooks(self) -> str | None:
        return """
useEffect(() => {
    const handle_key = (_e0) => {
        if (%s.includes(_e0.key))
            %s
    }
    document.addEventListener("keydown", handle_key, false);
    return () => {
        document.removeEventListener("keydown", handle_key, false);
    }
})
""" % (
            self.keys,
            rx.utils.format.format_event_chain(self.event_triggers["on_key_down"]),
        )

    def get_event_triggers(self) -> Dict[str, Any]:
        return {
            "on_key_down": lambda e0: [e0.key],
        }

    def render(self) -> str:
        return ""


def colored_box(color, index):
    return rx.box(bg=color, width="1em", height="1em", border="1px solid white")


def index():
    return rx.vstack(
        rx.hstack(
            rx.button(
                "PAUSE",
                on_click=State.turnOffTick,
                color_scheme="blue",
                border_radius="1em",
            ),
            rx.button(
                "RUN",
                on_click=State.turnOnTick,
                color_scheme="green",
                border_radius="1em",
            ),
            rx.switch(is_checked=State.running, on_change=State.flip_switch),
        ),
        rx.hstack(
            rx.vstack(
                rx.heading("RATE", font_size="1em"),
                rx.heading(State.rate, font_size="2em"),
                bg_color="yellow",
                border_width="1px",
                padding_left="1em",
                padding_right="1em",
            ),
            rx.vstack(
                rx.heading("SCORE", font_size="1em"),
                rx.heading(State.score, font_size="2em"),
                bg_color="yellow",
                border_width="1px",
                padding_left="1em",
                padding_right="1em",
            ),
            rx.vstack(
                rx.heading("MAGIC", font_size="1em"),
                rx.heading(State.magic, font_size="2em"),
                bg_color="yellow",
                border_width="1px",
                padding_left="1em",
                padding_right="1em",
            ),
        ),
        rx.cond(State.died, rx.heading("Game Over 🐍")),
        # Usage of foreach, please refer https://reflex.app/docs/library/layout/foreach
        rx.responsive_grid(
            rx.foreach(
                State.cells,
                lambda color, idx: colored_box(color, idx),
            ),
            columns=[N],
        ),
        GlobalKeyWatcher.create(
            keys=["ArrowUp", "ArrowLeft", "ArrowRight", "ArrowDown", ",", "."],
            on_key_down=State.handle_key,
        ),
        rx.hstack(
            rx.vstack(
                rx.button(
                    "￮",
                    on_click=State.arrow_none,
                    color_scheme="#FFFFFFFF",
                    border_radius="1em",
                    font_size="2em",
                ),
                rx.button(
                    "￩",
                    on_click=State.arrow_left,
                    color_scheme="red",
                    border_radius="1em",
                    font_size="2em",
                ),
            ),
            rx.vstack(
                rx.button(
                    "￪",
                    on_click=State.arrow_up,
                    color_scheme="red",
                    border_radius="1em",
                    font_size="2em",
                ),
                rx.button(
                    "￬",
                    on_click=State.arrow_down,
                    color_scheme="red",
                    border_radius="1em",
                    font_size="2em",
                ),
            ),
            rx.vstack(
                rx.button(
                    "￮",
                    on_click=State.arrow_none,
                    color_scheme="#FFFFFFFF",
                    border_radius="1em",
                    font_size="2em",
                ),
                rx.button(
                    "￫",
                    on_click=State.arrow_right,
                    color_scheme="red",
                    border_radius="1em",
                    font_size="2em",
                ),
            ),
        ),
        padding_top="3%",
    )


app = rx.App(state=State)
app.add_page(index, title="snake game")

app.compile()
