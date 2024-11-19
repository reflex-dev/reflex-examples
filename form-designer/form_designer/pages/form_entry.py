from typing import Any
import reflex as rx

from reflex_local_auth import LocalAuthState

from .. import routes, style
from ..components import field_view, navbar
from ..models import FieldType, FieldValue, Form, Response


Missing = object()


class FormEntryState(rx.State):
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

    def handle_submit(self, form_data: dict[str, Any]):
        response = Response(
            client_token=self._ensure_client_token(), form_id=self.form.id
        )
        for field in self.form.fields:
            value = form_data.get(field.name, Missing)
            if value and value is not Missing:
                response.field_values.append(
                    FieldValue(
                        field_id=field.id,
                        value=value,
                    )
                )
            elif field.type_ == FieldType.checkbox:
                field_values = []
                for option in field.options:
                    key = f"{field.name}___{option.value or option.label or option.id}"
                    value = form_data.get(key, Missing)
                    if value is not Missing:
                        field_values.append(
                            FieldValue(field_id=field.id, value=form_data[key])
                        )
                if field.required and not field_values:
                    return rx.toast(f"Field '{field.name}' is required.")
            elif field.required:
                return rx.toast(f"Field '{field.name}' is required.")
        with rx.session() as session:
            session.add(response)
            session.commit()
        return rx.redirect(routes.FORM_ENTRY_SUCCESS)


def authenticated_navbar(title_suffix: str | None = None):
    return rx.cond(
        LocalAuthState.is_authenticated,
        rx.fragment(
            navbar(title_suffix=title_suffix),
            rx.link("< Back", href=routes.edit_form(FormEntryState.form.id)),
        ),
    )


def form_entry_page():
    return style.layout(
        authenticated_navbar(title_suffix=f"Preview {FormEntryState.form.id}"),
        rx.form(
            rx.vstack(
                rx.center(rx.heading(FormEntryState.form.name)),
                rx.foreach(
                    FormEntryState.form.fields,
                    field_view,
                ),
                rx.button("Submit", type="submit"),
            ),
            on_submit=FormEntryState.handle_submit,
        ),
    )


def form_entry_success():
    return style.layout(
        authenticated_navbar(title_suffix=f"Saved {FormEntryState.form.id}"),
        rx.heading("Your response has been saved!"),
    )
