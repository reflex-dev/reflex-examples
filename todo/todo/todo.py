import pynecone as pc

class ListState(pc.State):
    items = ["Write Code", "Sleep", "Have Fun"]
    new_item: str

    def add_item(self):
        self.items += [self.new_item]
        self.new_item = ""

    def finish_item(self, item):
        self.items = [i for i in self.items if i != item]


def render_item(item):
    return pc.list_item(
        pc.hstack(
            pc.button(
                on_click=ListState.finish_item(item),
                height="1.5em",
                background_color="white",
                border="1px solid blue",
            ),
            pc.text(item, font_size="1.25em"),
        ),
    )


def todo_list():
    pc.vstack(
        pc.heading("Todos"),
        pc.input(
            value=ListState.new_item,
            placeholder="Add a todo...",
            bg="white",
        ),
        pc.button("Add", on_click=ListState.add_item, bg="white"),
        pc.divider(),
        pc.ordered_list(
            pc.foreach(
                ListState.items,
                lambda item : render_item(item),
            ),
        ),
        bg="#ededed",
        padding="1em",
        border_radius="0.5em",
        shadow="lg",
    )


app = pc.App(state=ListState)
app.add_page(todo_list)
app.compile()