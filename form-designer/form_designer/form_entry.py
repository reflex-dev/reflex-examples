import reflex as rx

from . import routes, style
from .field_view import field_view
from .models import FieldType, FieldValue, Form, Response
from .state import State


Missing = object()


class FormEntryState(State):
    form: Form = Form()
    client_token: str = rx.Cookie("")

    def _ensure_client_token(self):
        if self.client_token == "":
            self.client_token = self.router.session.client_token
        return self.client_token

    def load_form(self):
        if self.form_id != "":
            self.load_form_by_id(self.form_id)
        else:
            self.form = Form()

    def load_form_by_id(self, id_: int):
        with rx.session() as session:
            self.form = session.get(Form, id_)

    def handle_submit(self, form_data):
        response = Response(
            client_token=self._ensure_client_token(), form_id=self.form.id
        )
        for field in self.form.fields:
            value = form_data.get(field.name, Missing)
            if value is not Missing:
                response.field_values.append(
                    FieldValue(
                        field_id=field.id,
                        value=value,
                    )
                )
            elif field.type_ == FieldType.checkbox:
                for option in field.options:
                    key = f"{field.name}___{option.value or option.label}"
                    value = form_data.get(key, Missing)
                    if value is not Missing:
                        response.field_values.append(
                            FieldValue(field_id=field.id, value=form_data[key])
                        )
        with rx.session() as session:
            session.add(response)
            session.commit()
        return rx.redirect(routes.FORM_ENTRY_SUCCESS)


def form_entry():
    return rx.form(
        rx.vstack(
            rx.heading(FormEntryState.form.name),
            rx.foreach(
                FormEntryState.form.fields,
                field_view,
            ),
            rx.button("Submit", type_="submit"),
            **style.comfortable_margin,
        ),
        on_submit=FormEntryState.handle_submit,
    )


@rx.page(route=routes.FORM_ENTRY_SUCCESS)
def form_entry_success():
    return rx.heading("Your response has been saved!")
