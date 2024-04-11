import reflex as rx

from . import routes
from .form_editor import FormEditorState
from .models import Field, FieldType, Option
from .state import AppState


class FieldEditorState(AppState):
    field: Field = Field()
    form_owner_id: int = -1

    def _user_has_access(self):
        return self.form_owner_id == self.authenticated_user.id or self.is_admin

    def handle_submit(self, form_data: dict[str, str]):
        self.field.name = form_data["name"]
        self.field.type_ = form_data["type_"]
        self.field.required = bool(form_data.get("required"))
        return [
            FormEditorState.update_field(self.field),
            rx.redirect(routes.edit_form(self.form_id)),
        ]

    def handle_required_change(self, is_checked: bool):
        self.field.required = is_checked

    def handle_modal_open_change(self, is_open: bool):
        if not is_open:
            return rx.redirect(routes.edit_form(self.form_id))

    async def load_field(self):
        form_state = await self.get_state(FormEditorState)
        self.form_owner_id = form_state.form.owner_id
        if not self._user_has_access():
            return
        if self.field_id == "new":
            self.field = Field(form_id=self.form_id)
        else:
            with rx.session() as session:
                self.field = session.get(Field, self.field_id)

    def set_type(self, type_: str):
        self.field.type_ = FieldType(type_)

    def set_field(self, key: str, value: str):
        setattr(self.field, key, value)

    def set_option(self, index: int, key: str, value: str):
        if not self._user_has_access():
            return
        with rx.session() as session:
            session.add(self.field)
            if self.field.id is None:
                session.commit()
                session.refresh(self.field)
            option = self.field.options[index]
            option.field_id = self.field.id
            setattr(option, key, value)
            session.add(option)
            session.commit()
            session.refresh(self.field)

    def add_option(self):
        if not self._user_has_access():
            return
        with rx.session() as session:
            session.add(self.field)
            if not self.field.id:
                session.commit()
                session.refresh(self.field)
            option = Option(field_id=self.field.id)
            self.field.options.append(option)
            session.add(option)
            session.add(self.field)
            session.commit()
            session.refresh(self.field)

    def delete_option(self, index: int):
        if not self._user_has_access():
            return
        with rx.session() as session:
            session.add(self.field)
            option_to_delete = session.get(Option, self.field.options[index].id)
            if option_to_delete is not None:
                session.delete(option_to_delete)
            del self.field.options[index]
            session.commit()
            session.refresh(self.field)


def option_editor(option: Option, index: int):
    return rx.card(
        rx.hstack(
            rx.el.label(
                rx.text("Label"),
                rx.input(
                    placeholder="Label",
                    value=option.label,
                    on_change=lambda v: FieldEditorState.set_option(index, "label", v),
                ),
            ),
            rx.el.label(
                rx.text("Value"),
                rx.input(
                    placeholder=rx.cond(option.label != "", option.label, "Value"),
                    value=option.value,
                    on_change=lambda v: FieldEditorState.set_option(index, "value", v),
                ),
            ),
            rx.button(
                rx.icon(tag="x"),
                on_click=FieldEditorState.delete_option(index),
                type="button",
                color_scheme="tomato",
            ),
            align="end",
        ),
    )


def options_editor():
    return rx.vstack(
        rx.foreach(FieldEditorState.field.options, option_editor),
        rx.button("Add Option", on_click=FieldEditorState.add_option(), type="button"),
    )


def field_editor_input(key: str):
    return rx.el.label(
        key.capitalize(),
        rx.input(
            placeholder=key.capitalize(),
            name=key,
            value=getattr(FieldEditorState.field, key),
            on_change=lambda v: FieldEditorState.set_field(key, v),
        ),
        width="100%",
    )


def field_editor():
    return rx.form(
        rx.vstack(
            field_editor_input("name"),
            field_editor_input("prompt"),
            rx.el.label(
                rx.hstack(
                    "Type",
                    rx.select.root(
                        rx.select.trigger(),
                        rx.select.content(
                            *[rx.select.item(t.value, value=t.value or "unset") for t in FieldType],
                        ),
                        name="type_",
                        value=FieldEditorState.field.type_.to(str),
                        on_change=FieldEditorState.set_type,
                    ),
                )
            ),
            rx.el.label(
                rx.hstack(
                    "Required",
                    rx.checkbox(
                        name="required",
                        checked=FieldEditorState.field.required,
                        on_change=FieldEditorState.handle_required_change,
                    ),
                )
            ),
            rx.cond(
                rx.Var.create(
                    [
                        FieldType.select.value,
                        FieldType.radio.value,
                        FieldType.checkbox.value,
                    ]
                ).contains(FieldEditorState.field.type_),
                options_editor(),
            ),
            rx.button("Save", type="submit"),
            align="start",
        ),
        on_submit=FieldEditorState.handle_submit,
    )


def field_editor_modal():
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Edit Field"),
            field_editor()
        ),
        open=rx.State.field_id != "",
        on_open_change=FieldEditorState.handle_modal_open_change,
    )
