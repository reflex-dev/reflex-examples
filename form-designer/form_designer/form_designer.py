import reflex as rx

from . import routes
from .field_editor import FieldEditorState, field_editor_modal
from .form_editor import FormEditorState, form_editor
from .form_entry import FormEntryState, form_entry
from .form_select import form_select
from .response import ResponsesState, responses
from .state import State


TITLE = "Form Designer"


def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Form Designer"),
        rx.link("Create or Edit Forms", href=routes.FORM_EDIT_NEW),
    )


def form() -> rx.Component:
    return rx.vstack(
        rx.heading("Form Designer"),
        form_select(),
        form_editor(),
        rx.button(
            "Add Field",
            on_click=rx.redirect(routes.edit_field(State.form_id, "new")),
        ),
        field_editor_modal(),
    )


app = rx.App()
app.add_page(index, title=TITLE)
app.add_page(
    form,
    route=routes.FIELD_EDIT_ID,
    title=TITLE,
    on_load=[FormEditorState.load_form, FieldEditorState.load_field],
),
app.add_page(
    form,
    route=routes.FIELD_EDIT_NEW,
    title=TITLE,
    on_load=[FormEditorState.load_form, FieldEditorState.load_field],
),
app.add_page(
    form, route=routes.FORM_EDIT_ID, title=TITLE, on_load=FormEditorState.load_form
),
app.add_page(
    form, route=routes.FORM_EDIT_NEW, title=TITLE, on_load=FormEditorState.load_form
),
app.add_page(
    form_entry, route=routes.FORM_ENTRY, title=TITLE, on_load=FormEntryState.load_form
),
app.add_page(
    responses,
    route=routes.RESPONSES,
    title=TITLE,
    on_load=ResponsesState.load_responses,
)
app.compile()
