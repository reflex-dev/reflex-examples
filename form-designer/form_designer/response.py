import reflex as rx

from .field_view import field_prompt
from .models import Form, Response
from .state import State


class ResponsesState(State):
    form: Form = Form()
    responses: list[Response] = []

    def load_responses(self):
        with rx.session() as session:
            self.form = session.get(Form, self.form_id)
            self.responses = session.exec(
                Response.select.where(Response.form_id == self.form_id)
            ).all()


def response(r: Response):
    return rx.accordion_item(
        rx.accordion_button(r.client_token),
        rx.accordion_panel(
            rx.foreach(
                r.field_values,
                lambda fv: rx.vstack(
                    field_prompt(fv.field),
                    rx.cond(
                        fv.value != "",
                        rx.text(fv.value),
                        rx.text("No response provided."),
                    ),
                    align_items="flex-start",
                    margin_bottom="2em",
                ),
            ),
        ),
    )


def responses():
    return rx.vstack(
        rx.heading(ResponsesState.form.name),
        rx.accordion(
            rx.foreach(
                ResponsesState.responses,
                response,
            ),
            allow_toggle=True,
            allow_multiple=True,
        ),
    )
