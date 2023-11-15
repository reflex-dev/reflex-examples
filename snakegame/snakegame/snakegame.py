import asyncio
import random
from typing import Any, Dict, List

import reflex as rx
from reflex.utils.imports import ImportDict, ImportVar

N = 19  # There is a N*N grid for ground of snake
COLOR_NONE = "#EEEEEE"
COLOR_BODY = "#008800"
COLOR_FOOD = "#FF00FF"
COLOR_DEAD = "#FF0000"
# Tuples representing the directions the snake head can move
HEAD_U = (0, -1)
HEAD_D = (0, 1)
HEAD_L = (-1, 0)
HEAD_R = (1, 0)
INITIAL_SNAKE = [  # all (X,Y) for snake's body
    (-1, -1),
    (-1, -1),
    (-1, -1),
    (-1, -1),
    (-1, -1),
    (10, 15),  # Starting head position
]
INITIAL_FOOD = (5, 5)  # X, Y of food


def get_new_head(old_head: tuple[int, int], dir: tuple[int, int]) -> tuple[int, int]:
    """Calculate the new head position based on the given direction."""
    x, y = old_head
    return (x + dir[0] + N) % N, (y + dir[1] + N) % N


def to_cell_index(x: int, y: int) -> int:
    """Calculate the index into the game board for the given (X, Y)."""
    return x + N * y


class State(rx.State):
    dir: str = HEAD_R  # Direction the snake head is facing currently
    moves: list[tuple[int, int]] = []  # Queue of moves based on user input
    snake: list[tuple[int, int]] = INITIAL_SNAKE  # Body of snake
    food: tuple[int, int] = INITIAL_FOOD  # X, Y location of food
    cells: list[str] = (N * N) * [COLOR_NONE]  # The game board to be rendered
    score: int = 0  # Player score
    magic: int = 1  # Number of points per food eaten
    rate: int = 10  # 5 divide by rate determines tick period
    died: bool = False  # If the snake is dead (game over)
    tick_cnt: int = 1  # How long the game has been running
    running: bool = False
    _n_tasks: int = 0

    def play(self):
        """Start / resume the game."""
        if not self.running:
            if self.died:
                # If the player is dead, reset game state before beginning.
                self.reset()
            self.running = True
            return State.loop

    def pause(self):
        """Signal the game to pause."""
        self.running = False

    def flip_switch(self, start):
        """Toggle whether the game is running or paused."""
        if start:
            return State.play
        else:
            return State.pause

    def _next_move(self):
        """Returns the next direction the snake head should move in."""
        return self.moves[0] if self.moves else self.dir

    def _last_move(self):
        """Returns the last queued direction the snake head should move in."""
        return self.moves[-1] if self.moves else self.dir

    @rx.background
    async def loop(self):
        """The main game loop, implemented as a singleton background task.

        Responsible for updating the game state on each tick.
        """
        async with self:
            if self._n_tasks > 0:
                # Only start one loop task at a time.
                return
            self._n_tasks += 1

        while self.running:
            # Sleep based on the current rate
            await asyncio.sleep(5 / self.rate)
            async with self:
                # Which direction will the snake move?
                self.dir = self._next_move()
                if self.moves:
                    # Remove the processed next move from the queue
                    del self.moves[0]

                # Calculate new head position
                head = get_new_head(self.snake[-1], dir=self.dir)
                if head in self.snake:
                    # New head position crashes into snake body, Game Over
                    self.running = False
                    self.died = True
                    self.cells[to_cell_index(*head)] = COLOR_DEAD
                    break

                # Move the snake
                self.snake.append(head)
                self.cells[to_cell_index(*head)] = COLOR_BODY
                food_eaten = False
                while self.food in self.snake:
                    food_eaten = True
                    self.food = (random.randint(0, N - 1), random.randint(0, N - 1))
                self.cells[to_cell_index(*self.food)] = COLOR_FOOD
                if not food_eaten:
                    # Advance the snake
                    self.cells[to_cell_index(*self.snake[0])] = COLOR_NONE
                    del self.snake[0]
                else:
                    # Grow the snake (and the score)
                    self.score += self.magic
                    self.magic += 1
                    self.rate = 10 + self.magic
                self.tick_cnt += 1

        async with self:
            # Decrement task counter, since we're about to return
            self._n_tasks -= 1

    def arrow_up(self):
        """Queue a move up."""
        if self._last_move() != HEAD_D:
            self.moves.append(HEAD_U)

    def arrow_left(self):
        """Queue a move left."""
        if self._last_move() != HEAD_R:
            self.moves.append(HEAD_L)

    def arrow_right(self):
        """Queue a move right."""
        if self._last_move() != HEAD_L:
            self.moves.append(HEAD_R)

    def arrow_down(self):
        """Queue a move down."""
        if self._last_move() != HEAD_U:
            self.moves.append(HEAD_D)

    def arrow_rel_left(self):
        """Queue a move left relative to the current direction."""
        last_move = self._last_move()
        if last_move == HEAD_U:
            self.arrow_left()
        elif last_move == HEAD_L:
            self.arrow_down()
        elif last_move == HEAD_D:
            self.arrow_right()
        elif last_move == HEAD_R:
            self.arrow_up()

    def arrow_rel_right(self):
        """Queue a move right relative to the current direction."""
        last_move = self._last_move()
        if last_move == HEAD_U:
            self.arrow_right()
        elif last_move == HEAD_L:
            self.arrow_up()
        elif last_move == HEAD_D:
            self.arrow_left()
        elif last_move == HEAD_R:
            self.arrow_down()

    def handle_key(self, key):
        """Handle keyboard press."""
        {
            "ArrowUp": self.arrow_up,
            "ArrowLeft": self.arrow_left,
            "ArrowRight": self.arrow_right,
            "ArrowDown": self.arrow_down,
            ",": self.arrow_rel_left,
            ".": self.arrow_rel_right,
        }[key]()


class GlobalKeyWatcher(rx.Fragment):
    """A component that attaches a keydown handler to the document.

    The handler only calls the backend function if the pressed key is one of the
    specified keys.

    Requires custom javascript to support this functionality at the moment.
    """

    # List of keys to trigger on
    keys: rx.vars.Var[List[str]] = []

    def _get_imports(self) -> ImportDict:
        return {
            **super()._get_imports(),
            "react": {ImportVar(tag="useEffect")},
        }

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
        # This component has no visual element.
        return ""


def colored_box(color, index):
    """One square of the game grid."""
    return rx.box(bg=color, width="1em", height="1em", border="1px solid white")


def stat_box(label, value):
    """One of the score, magic, or rate boxes."""
    return rx.vstack(
        rx.heading(label, font_size="1em"),
        rx.heading(value, font_size="2em"),
        bg_color="yellow",
        border_width="1px",
        padding_left="1em",
        padding_right="1em",
    )


def control_button(label, on_click):
    """One of the arrow buttons for touch/mouse control."""
    return rx.button(
        label,
        on_click=on_click,
        color_scheme="red",
        border_radius="1em",
        font_size="2em",
    )


def padding_button():
    """A button that is used for padding in the controls panel."""
    return rx.button(
        "￮",
        color_scheme="none",
        border_radius="1em",
        font_size="2em",
    )


def controls_panel():
    """The controls panel of arrow buttons."""
    return rx.hstack(
        GlobalKeyWatcher.create(
            keys=["ArrowUp", "ArrowLeft", "ArrowRight", "ArrowDown", ",", "."],
            on_key_down=State.handle_key,
        ),
        rx.vstack(
            padding_button(),
            control_button(
                "￩",
                on_click=State.arrow_left,
            ),
        ),
        rx.vstack(
            control_button(
                "￪",
                on_click=State.arrow_up,
            ),
            control_button(
                "￬",
                on_click=State.arrow_down,
            ),
        ),
        rx.vstack(
            padding_button(),
            control_button(
                "￫",
                on_click=State.arrow_right,
            ),
        ),
    )


def index():
    return rx.vstack(
        rx.hstack(
            rx.button(
                "PAUSE",
                on_click=State.pause,
                color_scheme="blue",
                border_radius="1em",
            ),
            rx.button(
                "RUN",
                on_click=State.play,
                color_scheme="green",
                border_radius="1em",
            ),
            rx.switch(is_checked=State.running, on_change=State.flip_switch),
        ),
        rx.hstack(
            stat_box("RATE", State.rate),
            stat_box("SCORE", State.score),
            stat_box("MAGIC", State.magic),
        ),
        # Usage of foreach, please refer https://reflex.app/docs/library/layout/foreach
        rx.responsive_grid(
            rx.foreach(
                State.cells,
                lambda color, idx: colored_box(color, idx),
            ),
            columns=[N],
        ),
        rx.cond(State.died, rx.heading("Game Over 🐍")),
        controls_panel(),
        padding_top="3%",
    )


app = rx.App(state=State)
app.add_page(index, title="snake game")

app.compile()
