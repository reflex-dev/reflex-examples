import reflex as rx


class State(rx.State):
    """The app state."""

    # The current items in the todo list.
    items = ["Write Code", "Sleep", "Have Fun"]

    # The new item to add to the todo list.
    new_item: str

    def add_item(self):
        """Add a new item to the todo list."""
        if self.new_item:
            self.items.append(self.new_item)
            # Clear the value of the input.
            self.new_item = ""

    def finish_item(self, item: str):
        """Finish an item in the todo list.

        Args:
            item: The item to finish.
        """
        self.items.pop(self.items.index(item))


def todo_item(item: rx.Var[str]) -> rx.Component:
    """Render an item in the todo list.

    NOTE: When using `rx.foreach`, the item will be a Var[str] rather than a str.

    Args:
        item: The todo list item.

    Returns:
        A single rendered todo list item.
    """
    return rx.list_item(
        # A button to finish the item.
        rx.button("✓",
                  on_click=lambda: State.finish_item(item),
                  margin="0 1em 1em 0"
                  ),
        # The item text.
        rx.text(item, as_="span"),
    )


def todo_list() -> rx.Component:
    """Render the todo list.

    Returns:
        The rendered todo list.
    """
    return rx.ordered_list(
        # rx.foreach is necessary to iterate over state vars.
        # see: https://reflex.dev/docs/library/layout/foreach
        rx.foreach(State.items, lambda item: todo_item(item)),
    )


def new_item() -> rx.Component:
    """Render the new item form.

    See: https://reflex.dev/docs/library/forms/form

    Returns:
        A form to add a new item to the todo list.
    """
    return rx.hstack(rx.input(
        id="new_item",
        placeholder="Add a todo...",
        bg="white",
        on_change=State.set_new_item,
        value=State.new_item,
    ),
        rx.button("Add", on_click=State.add_item),
    )


def index() -> rx.Component:
    """A view of the todo list.

    Returns:
        The index page of the todo app.
    """
    return rx.container(
        rx.vstack(
            rx.heading("Todos"),
            new_item(),
            rx.divider(),
            todo_list(),
            bg=rx.color("gray", 7),
            margin_top="5em",
            margin_x="25vw",
            padding="1em",
            border_radius="0.5em",
            box_shadow=f"{rx.color('gray', 3, alpha=True)} 0px 1px 4px",
        )
    )


# Create the app and add the state.
app = rx.App()

# Add the index page and set the title.
app.add_page(index, title="Todo App")
