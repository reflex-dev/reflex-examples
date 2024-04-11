import reflex as rx

from . import routes
from .field_view import field_input, field_prompt
from .form_select import FormSelectState
from .models import Field, FieldValue, Form, Option


class FormEditorState(rx.State):
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
    return rx.card(
        rx.hstack(
            rx.link(
                field_prompt(field, show_name=True),
                href=routes.edit_field(rx.State.form_id, field.id),
            ),
            rx.spacer(),
            rx.tooltip(
                rx.link(rx.icon(tag="x"), on_click=FormEditorState.delete_field(field.id)),
                content="Delete Field",
            ),
            margin_bottom="12px",
        ),
        rx.hstack(
            field_input(field),
            rx.text(rx.cond(field.required, "(required)", "(optional)"), size="1", ml="3"),
            justify="between",
        ),
        width="100%",
    )


def form_editor():
    return rx.vstack(
        rx.hstack(
            rx.el.label(
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
                rx.hstack(
                    rx.button(
                        "Preview",
                        on_click=rx.redirect(routes.show_form(FormEditorState.form.id)),
                        type="button",
                    ),
                    rx.button(
                        "Responses",
                        on_click=rx.redirect(
                            routes.form_responses(FormEditorState.form.id)
                        ),
                    ),
                    rx.spacer(),
                    rx.button(
                        "Delete Form",
                        color_scheme="tomato",
                        on_click=FormEditorState.delete_form, type="button",
                    ),
                    width="100%",
                ),
            ),
            align="end",
            justify="start",
            width="100%",
        ),
        rx.divider(),
        rx.foreach(
            FormEditorState.form.fields,
            field_edit_view,
        ),
        width="100%",
    )
