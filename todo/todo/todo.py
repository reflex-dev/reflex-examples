import reflex as rx
import reflex.components.radix.themes as rdxt


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
        rx.hstack(
            # A button to finish the item.
            rdxt.button(
                on_click=lambda: State.finish_item(item),
                height="1.5em",
                background_color="white",
                border="1px solid blue",
            ),
            # The item text.
            rdxt.text(item, font_size="1.25em"),
        )
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

    # TODO update to Radix form URL
    See: https://reflex.dev/docs/library/forms/form

    Returns:
        A form to add a new item to the todo list.
    """
    return rdxt.textfield_root(
        rdxt.textfield_input(
            placeholder="What to do...?",
            value=State.new_item,
            on_change=State.set_new_item,
            size="3"
        ),
        rdxt.textfield_slot(
            rdxt.button("Add", size="2",  on_click=State.add_item),
        ),
    )


def index() -> rx.Component:
    """A view of the todo list.

    Returns:
        The index page of the todo app.
    """
    return rx.container(
        rx.vstack(
            rdxt.heading("Todos"),
            new_item(),
            rdxt.separator(),
            todo_list(),
            bg="#ededed",
            margin="5em",
            padding="1em",
            border_radius="0.5em",
            shadow="lg",
        )
    )


# Create the app and add the state.
app = rx.App(
    theme=rdxt.theme(
        appearance="light", has_background=True, radius="medium", high_contrast=True,
    ),
)

# Add the index page and set the title.
app.add_page(index, title="Todo App")
