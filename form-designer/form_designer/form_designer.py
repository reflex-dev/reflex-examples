from pathlib import Path

import reflex as rx

import reflex_local_auth

from . import routes, style
from .field_editor import FieldEditorState, field_editor_modal
from .form_editor import FormEditorState, form_editor
from .form_entry import FormEntryState, form_entry
from .form_select import form_select
from .response import ResponsesState, responses


TITLE = "Form Designer"


def navbar_menu() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(rx.icon("menu", size=20), cursor="pointer"),
        rx.menu.content(
            rx.cond(
                reflex_local_auth.LocalAuthState.is_authenticated,
                rx.fragment(
                    rx.hstack(
                        rx.avatar(
                            fallback=reflex_local_auth.LocalAuthState.authenticated_user.username[0],
                            size="1",
                        ),
                        rx.text(reflex_local_auth.LocalAuthState.authenticated_user.username),
                        margin="8px",
                    ),
                    rx.menu.separator(),
                ),
            ),
            rx.menu.item("Home", on_click=rx.redirect("/")),
            rx.cond(
                reflex_local_auth.LocalAuthState.is_authenticated,
                rx.menu.item(
                    "Logout",
                    on_click=[
                        reflex_local_auth.LocalAuthState.do_logout,
                        rx.redirect("/"),
                    ],
                ),
                rx.fragment(
                    rx.menu.item("Register", on_click=rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE)),
                    rx.menu.item("Login", on_click=rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)),
                ),
            ),
            rx.menu.separator(),
            rx.hstack(
                rx.icon("sun", size=16),
                rx.color_mode.switch(size="1"),
                rx.icon("moon", size=16),
                margin="8px",
            ),
        )
    )


def navbar() -> rx.Component:
    return rx.hstack(
        rx.heading("Form Designer"),
        rx.spacer(),
        navbar_menu(),
        margin_y="12px",
        align="center",
    )


def index() -> rx.Component:
    readme_content = Path(__file__).resolve().parent.parent / "README.md"
    return style.layout(
        navbar(),
        rx.link("Create or Edit Forms", href=routes.FORM_EDIT_NEW),
        rx.divider(),
        rx.card(
            rx.inset(
                rx.badge(rx.code("README.md"), width="100%", size="2"),
                side="top",
                pb="current",
                clip="padding-box",
            ),
            rx.markdown(readme_content.read_text()),
            margin_y="2em",
        )
    )


@reflex_local_auth.require_login
def form() -> rx.Component:
    return style.layout(
        navbar(),
        rx.hstack(
            form_select(),
            rx.button(
                "New Form",
                on_click=rx.redirect(routes.FORM_EDIT_NEW),
                type="button",
            ),
            width="100%",
        ),
        rx.divider(),
        form_editor(),
        rx.cond(
            rx.State.form_id != "",
            rx.fragment(
                rx.button(
                    "Add Field",
                    on_click=rx.redirect(routes.edit_field(rx.State.form_id, "new")),
                    is_disabled=rx.State.form_id == "",
                    type="button",
                ),
                field_editor_modal(),
            ),
        ),
        rx.logo(height="3em", margin_bottom="12px"),
    )


def quoted_var(value: str) -> rx.Var:
    return rx.Var.create(f"'{value}'", _var_is_local=True)


app = rx.App(theme=rx.theme(accent_color="blue"))
app.add_page(index, title=TITLE)


# Authentication via reflex-local-auth
app.add_page(
    reflex_local_auth.pages.login_page,
    route=reflex_local_auth.routes.LOGIN_ROUTE,
    title="Login",
)
app.add_page(
    reflex_local_auth.pages.register_page,
    route=reflex_local_auth.routes.REGISTER_ROUTE,
    title="Register",
)


rx.State.add_var("form_id", str, "")
rx.State.add_var("field_id", str, "")


def field_edit_title():
    form_name = rx.cond(
        rx.State.form_id == "",
        quoted_var("New Form"),
        rx.cond(
            FormEditorState.form, FormEditorState.form.name, quoted_var("Unknown Form")
        ),
    )
    field_name = rx.cond(
        rx.State.field_id == "",
        quoted_var("New Field"),
        rx.cond(
            FieldEditorState.field,
            FieldEditorState.field.name,
            quoted_var("Unknown Field"),
        ),
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
        rx.State.form_id == "",
        quoted_var("New Form"),
        rx.cond(
            FormEditorState.form, FormEditorState.form.name, quoted_var("Unknown Form")
        ),
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
        rx.State.form_id == "",
        quoted_var("Unknown Form"),
        FormEntryState.form.name,
    ),
    on_load=FormEntryState.load_form,
)


def responses_title():
    form_name = rx.cond(
        rx.State.form_id == "",
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
