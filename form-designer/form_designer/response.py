import reflex as rx

from . import style
from .field_view import field_prompt
from .models import Form, Response


class ResponsesState(rx.State):
    form: Form = Form()
    responses: list[Response] = []

    def load_responses(self):
        with rx.session() as session:
            self.form = session.get(Form, self.form_id)
            self.responses = session.exec(
                Response.select.where(Response.form_id == self.form_id)
            ).all()

    def delete_response(self, id: int):
        with rx.session() as session:
            session.delete(session.get(Response, id))
            session.commit()
            return ResponsesState.load_responses


def response(r: Response):
    return rx.accordion_item(
        rx.accordion_button(
            rx.hstack(
                rx.text(r.client_token),
                rx.accordion_icon(),
                rx.spacer(),
                rx.button("Delete", on_click=ResponsesState.delete_response(r.id)),
                width="100%",
            )
        ),
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
            width="100%",
        ),
        **style.comfortable_margin,
    )
