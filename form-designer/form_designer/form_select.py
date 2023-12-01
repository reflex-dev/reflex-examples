import reflex as rx
import reflex.components.radix.themes as rdxt

from . import routes
from .models import Form


class FormSelectState(rx.State):
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

    return rdxt.selectroot(
        rdxt.selecttrigger(placeholder="Existing Forms"),
        rdxt.selectcontent(
            rx.foreach(
                FormSelectState.forms, lambda form: rdxt.selectitem(form.name, value=form.id.to_string())
            ),
        ),
        value=rx.State.form_id,
        on_value_change=FormSelectState.on_select_change,
        on_mount=FormSelectState.load_forms,
    )
