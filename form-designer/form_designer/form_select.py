import reflex as rx

from . import routes
from .models import Form
from .state import AppState


class FormSelectState(AppState):
    forms: list[Form] = []

    def load_forms(self):
        if not self.is_authenticated:
            return
        with rx.session() as session:
            self.forms = session.exec(Form.select().where(Form.owner_id == self.authenticated_user.id)).all()

    def on_select_change(self, value: str):
        if value == "":
            return rx.redirect(routes.FORM_EDIT_NEW)
        return rx.redirect(routes.edit_form(value))


def form_select():
    return rx.box(
        rx.select.root(
            rx.select.trigger(placeholder="Existing Forms", width="100%"),
            rx.select.content(
                rx.foreach(
                    FormSelectState.forms, lambda form: rx.select.item(form.name, value=form.id.to_string())
                ),
            ),
            value=rx.State.form_id,
            on_change=FormSelectState.on_select_change,
            on_mount=FormSelectState.load_forms,
        ),
        width="100%",
    )
