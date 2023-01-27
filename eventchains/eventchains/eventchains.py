import asyncio
import pynecone as pc


class State(pc.State):
    """The app state."""

    is_loading: bool = False
    counter: int = 0

    def toggle_loading(self):
        self.is_loading = not self.is_loading

    async def increment(self):
        await asyncio.sleep(1)
        self.counter += 2


def index():
    return pc.vstack(
        pc.box(State.counter),
        pc.button(
            "Increment",
            on_click=[State.toggle_loading, State.increment, State.toggle_loading],
            is_loading=State.is_loading,
        ),
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.compile()
