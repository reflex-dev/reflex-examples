import pynecone as pc


class State(pc.State):
    items = ["Write Code", "Sleep", "Have Fun"]
    new_item: str

    def add_item(self):
        self.items += [self.new_item]
        self.new_item = ""

    def finish_item(self, item):
        self.items = [i for i in self.items if i != item]


def render_item(item):
    """Render an item in the todo list."""
    return pc.list_item(
        pc.hstack(
            pc.button(
                on_click=lambda: State.finish_item(item),
                height="1.5em",
                background_color="white",
                border="1px solid blue",
            ),
            pc.text(item, font_size="1.25em"),
        )
    )


def todo_list():
    """A view of the todo list."""
    return pc.container(
        pc.vstack(
            pc.heading("Todos"),
            pc.input(
                on_blur=State.set_new_item,
                placeholder="Add a todo...",
                bg="white",
            ),
            pc.button("Add", on_click=State.add_item, bg="white"),
            pc.divider(),
            pc.ordered_list(
                pc.foreach(State.items, lambda item: render_item(item)),
            ),
            bg="#ededed",
            margin="5em",
            padding="1em",
            border_radius="0.5em",
            shadow="lg",
        )
    )


app = pc.App(state=State)
app.add_page(todo_list, path="/")
app.compile()
