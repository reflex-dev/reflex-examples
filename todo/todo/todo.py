import pynecone as pc


class State(pc.State):
    """The app state."""

    # The current items in the todo list.
    items = ["Write Code", "Sleep", "Have Fun"]

    # The new item to add to the todo list.
    new_item: str

    def add_item(self, form_data: dict[str, str]):
        """Add a new item to the todo list.

        Args:
            form_data: The data from the form.
        """
        # Add the new item to the list.
        self.items.append(form_data["new_item"])

        # Clear the value of the input.
        return pc.set_value("new_item", "")

    def finish_item(self, item: str):
        """Finish an item in the todo list.

        Args:
            item: The item to finish.
        """
        self.items.pop(self.items.index(item))


def todo_item(item: pc.Var[str]) -> pc.Component:
    """Render an item in the todo list.

    NOTE: When using `pc.foreach`, the item will be a Var[str] rather than a str.

    Args:
        item: The todo list item.

    Returns:
        A single rendered todo list item.
    """
    return pc.list_item(
        pc.hstack(
            # A button to finish the item.
            pc.button(
                on_click=lambda: State.finish_item(item),
                height="1.5em",
                background_color="white",
                border="1px solid blue",
            ),
            # The item text.
            pc.text(item, font_size="1.25em"),
        )
    )


def todo_list() -> pc.Component:
    """Render the todo list.

    Returns:
        The rendered todo list.
    """
    return pc.ordered_list(
        # pc.foreach is necessary to iterate over state vars.
        # see: https://pynecone.io/docs/library/layout/foreach
        pc.foreach(State.items, lambda item: todo_item(item)),
    )


def new_item() -> pc.Component:
    """Render the new item form.

    See: https://pynecone.io/docs/library/forms/form

    Returns:
        A form to add a new item to the todo list.
    """
    return pc.form(
        # Pressing enter will submit the form.
        pc.input(
            id="new_item",
            placeholder="Add a todo...",
            bg="white",
        ),
        # Clicking the button will also submit the form.
        pc.center(
            pc.button("Add", type_="submit", bg="white"),
        ),
        on_submit=State.add_item,
    )


def index() -> pc.Component:
    """A view of the todo list.

    Returns:
        The index page of the todo app.
    """
    return pc.container(
        pc.vstack(
            pc.heading("Todos"),
            new_item(),
            pc.divider(),
            todo_list(),
            bg="#ededed",
            margin="5em",
            padding="1em",
            border_radius="0.5em",
            shadow="lg",
        )
    )


# Create the app and add the state.
app = pc.App(state=State)

# Add the index page and set the title.
app.add_page(index, title="Todo App")

# Compile the app.
app.compile()
