import warnings

# reflex_local_auth.LocalUser still subclasses the deprecated rx.Model;
# suppress the resulting warning until upstream migrates to SQLModel.
warnings.filterwarnings(
    "ignore",
    message="reflex.Model has been deprecated.*",
    category=DeprecationWarning,
)
# reflex's deprecation message uses console.deprecate (which print()s directly)
# rather than warnings.warn, so also patch that path.
from reflex_base.utils import console as _rx_console  # noqa: E402

_rx_console_deprecate_orig = _rx_console.deprecate


def _rx_console_deprecate(*, feature_name, **kwargs):
    if feature_name == "reflex.Model":
        return
    return _rx_console_deprecate_orig(feature_name=feature_name, **kwargs)


_rx_console.deprecate = _rx_console_deprecate

import reflex as rx  # noqa: E402

import reflex_local_auth  # noqa: E402

from . import constants, routes
from .components import (
    FieldEditorState,
    FormEditorState,
    field_edit_title,
    form_edit_title,
)
from .pages import (
    FormEntryState,
    ResponsesState,
    form_editor_page,
    home_page,
    form_entry_page,
    form_entry_success,
    responses_page,
    responses_title,
)

app = rx.App()
app.add_page(home_page, route="/", title=constants.TITLE)

# Register the dynamic route vars.
rx.State.setup_dynamic_args(rx.app.get_route_args("/_dummy/[form_id]/[field_id]"))

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

# Field editing routes
app.add_page(
    form_editor_page,
    route=routes.FIELD_EDIT_ID,
    title=field_edit_title(),
    on_load=[FormEditorState.load_form, FieldEditorState.load_field],
)
app.add_page(
    form_editor_page,
    route=routes.FIELD_EDIT_NEW,
    title=field_edit_title(),
    on_load=[FormEditorState.load_form, FieldEditorState.load_field],
)

# Form editing routes
app.add_page(
    form_editor_page,
    route=routes.FORM_EDIT_ID,
    title=form_edit_title(),
    on_load=FormEditorState.load_form,
)
app.add_page(
    form_editor_page,
    route=routes.FORM_EDIT_NEW,
    title=form_edit_title(),
    on_load=FormEditorState.load_form,
)

# Form entry routes
app.add_page(
    form_entry_page,
    route=routes.FORM_ENTRY,
    title=rx.cond(
        rx.State.form_id == "",
        "Unknown Form",
        FormEntryState.form.name,
    ),
    on_load=FormEntryState.load_form,
)
app.add_page(
    form_entry_success,
    route=routes.FORM_ENTRY_SUCCESS,
    title="Form Response Saved",
)

# Response viewing routes
app.add_page(
    responses_page,
    route=routes.RESPONSES,
    title=responses_title(),
    on_load=ResponsesState.load_responses,
)

# Create the database if it does not exist (hosting service does not migrate automatically)
import sqlmodel as _sqlmodel
from reflex.model import get_engine as _get_engine

_sqlmodel.SQLModel.metadata.create_all(_get_engine())
