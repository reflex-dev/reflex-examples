import reflex as rx

from . import routes
from .field_view import field_input, field_prompt
from .form_select import FormSelectState
from .models import Field, FieldValue, Form, Option
from .state import State


class FormEditorState(State):
    form: Form = Form()

    def load_form(self):
        if self.form_id != "":
            self.load_form_by_id(self.form_id)
        else:
            self.form = Form()

    def load_form_by_id(self, id_: int):
        with rx.session() as session:
            self.form = session.get(Form, id_)

    def delete_form(self):
        if self.form.id is not None:
            with rx.session() as session:
                session.delete(session.get(Form, self.form_id))
                session.commit()
                yield rx.redirect(routes.FORM_EDIT_NEW)

    def set_name(self, name: str):
        with rx.session() as session:
            self.form.name = name
            session.add(self.form)
            session.commit()
            session.refresh(self.form)
            if self.form_id == "":
                return rx.redirect(routes.edit_form(self.form.id))
            return FormSelectState.load_forms

    def update_field(self, field: Field):
        field.pop("options", None)  # Remove options, relationship
        field = Field(**field)
        with rx.session() as session:
            session.add(self.form)
            session.commit()
            if field.id is None:
                self.form.fields.append(field)
                session.add(field)
                session.add(self.form)
                session.commit()
            else:
                for existing_field in self.form.fields:
                    if existing_field.id == field.id:
                        existing_field.name = field.name
                        existing_field.type_ = field.type_
                        existing_field.required = field.required
                        existing_field.prompt = field.prompt
                        session.add(existing_field)
                        session.commit()
            return FormEditorState.load_form_by_id(self.form.id)

    def delete_field(self, field_id):
        with rx.session() as session:
            session.delete(session.get(Field, field_id))
            session.commit()
            return FormEditorState.load_form_by_id(self.form.id)


def field_edit_view(field: Field):
    return rx.box(
        rx.hstack(
            rx.link(
                field_prompt(field, show_name=True),
                href=routes.edit_field(State.form_id, field.id),
            ),
            rx.spacer(),
            rx.link("X", on_click=FormEditorState.delete_field(field.id)),
        ),
        field_input(field),
        rx.text(rx.cond(field.required, "Required", "Optional")),
        border="1px solid black",
        padding="5px",
        width="100%",
    )


def form_editor():
    return rx.vstack(
        rx.hstack(
            rx.form_label(
                "Form Name",
                rx.input(
                    placeholder="Form Name",
                    name="name",
                    value=FormEditorState.form.name,
                    on_change=FormEditorState.set_name,
                    debounce_timeout=1000,
                ),
            ),
            rx.cond(
                FormEditorState.form_id != "",
                rx.button("Delete Form", on_click=FormEditorState.delete_form),
            ),
        ),
        rx.cond(
            FormEditorState.form_id != "",
            rx.hstack(
                rx.button(
                    "Preview",
                    on_click=rx.redirect(routes.show_form(FormEditorState.form.id)),
                ),
                rx.button(
                    "Responses",
                    on_click=rx.redirect(
                        routes.form_responses(FormEditorState.form.id)
                    ),
                ),
            ),
        ),
        rx.foreach(
            FormEditorState.form.fields,
            field_edit_view,
        ),
        width="100%",
    )
