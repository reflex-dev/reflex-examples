import reflex as rx
import reflex.components.radix.primitives as rdxp
import reflex.components.radix.themes as rdxt

from . import common as cm, style
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
    return rdxp.accordion_item(
        cm.hstack(
            rdxt.text(r.client_token),
            rdxt.button(
                rdxt.icon(tag="cross_2"),
                color_scheme="tomato",
                margin_right="1em",
                on_click=ResponsesState.delete_response(r.id),
            ),
            width="100%",
            justify="between",
        ),
        rx.foreach(
            r.field_values,
            lambda fv: cm.vstack(
                field_prompt(fv.field),
                rx.cond(
                    fv.value != "",
                    rdxt.text(fv.value),
                    rdxt.text("No response provided."),
                ),
                align="start",
                m="2",
            ),
        ),
        value=r.id.to(str),
    )


def responses():
    return cm.vstack(
        rdxt.heading(ResponsesState.form.name),
        rdxp.accordion(
            rx.foreach(
                ResponsesState.responses,
                response,
            ),
            collapsible=True,
            type_="multiple",
            width="100%",
        ),
        **style.comfortable_margin,
    )
