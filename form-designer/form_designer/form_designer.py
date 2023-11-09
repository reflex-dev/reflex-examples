import reflex as rx

from . import routes, style
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
        **style.comfortable_margin,
    )


def form() -> rx.Component:
    return rx.vstack(
        rx.heading("Form Designer"),
        form_select(),
        form_editor(),
        rx.button(
            "Add Field",
            on_click=rx.redirect(routes.edit_field(State.form_id, "new")),
            is_disabled=State.form_id == "",
        ),
        field_editor_modal(),
        **style.comfortable_margin,
    )


def quoted_var(value: str) -> rx.Var:
    return rx.Var.create(f"'{value}'", _var_is_local=True)


app = rx.App()
app.add_page(index, title=TITLE)


def field_edit_title():
    form_name = rx.cond(
        State.form_id == "",
        quoted_var("New Form"),
        FormEditorState.form.name,
        )
    field_name = rx.cond(
        State.field_id == "",
        quoted_var("New Field"),
        FieldEditorState.field.name,
        )
    return f"{TITLE} | {form_name} | {field_name}"


app.add_page(
    form,
    route=routes.FIELD_EDIT_ID,
    title=field_edit_title(),
    on_load=[FormEditorState.load_form, FieldEditorState.load_field],
)
app.add_page(
    form,
    route=routes.FIELD_EDIT_NEW,
    title=field_edit_title(),
    on_load=[FormEditorState.load_form, FieldEditorState.load_field],
)


def form_edit_title():
    form_name = rx.cond(
        State.form_id == "",
        quoted_var("New Form"),
        FormEditorState.form.name,
        )
    return f"{TITLE} | {form_name}"


app.add_page(
    form,
    route=routes.FORM_EDIT_ID,
    title=form_edit_title(),
    on_load=FormEditorState.load_form,
)
app.add_page(
    form,
    route=routes.FORM_EDIT_NEW,
    title=form_edit_title(),
    on_load=FormEditorState.load_form,
)


app.add_page(
    form_entry,
    route=routes.FORM_ENTRY,
    title=rx.cond(
        State.form_id == "",
        quoted_var("Unknown Form"),
        FormEntryState.form.name,
    ),
    on_load=FormEntryState.load_form,
)



def responses_title():
    form_name = rx.cond(
        State.form_id == "",
        quoted_var("Unknown Form"),
        ResponsesState.form.name,
        )
    return f"{TITLE} | {form_name} | Responses"


app.add_page(
    responses,
    route=routes.RESPONSES,
    title=responses_title(),
    on_load=ResponsesState.load_responses,
)

app.compile()
