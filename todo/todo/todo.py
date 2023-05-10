import pynecone as pc


class State(pc.State):
    items = ["Write Code", "Sleep", "Have Fun"]
    new_item: str = ""
    async def add_item(self):
        added_item:str = self.new_item
        added_item = added_item.lstrip().rstrip()
        if(added_item == ""):
            self.new_item = ""
        elif added_item not in self.items:
            self.items += [added_item]
            self.new_item = ""
        else:
            self.new_item = added_item
            return pc.window_alert("The item you entered is duplicated.")

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
                placeholder="Add a todo...",
                bg="white",
                value=State.new_item,
                on_change=State.set_new_item,
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
app.add_page(todo_list, route="/")
app.compile()
