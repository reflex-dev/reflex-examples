import reflex as rx

from . import routes
from .models import Form
from .state import State


class FormSelectState(State):
    forms: list[Form] = []

    def load_forms(self):
        with rx.session() as session:
            self.forms = session.exec(Form.select).all()

    def on_select_change(self, value: str):
        if value == "":
            return rx.redirect(routes.FORM_EDIT_NEW)
        return rx.redirect(routes.edit_form(value))


def form_select():
    from .form_editor import FormEditorState

    return rx.select(
        rx.option("New Form", value=""),
        rx.foreach(
            FormSelectState.forms, lambda form: rx.option(form.name, value=form.id)
        ),
        value=State.form_id,
        on_change=FormSelectState.on_select_change,
        on_mount=FormSelectState.load_forms,
    )
