import reflex as rx

from .register import add_register_push_endpoint, trigger_register
from .state import PushState


def registration_status():
    return rx.cond(
        PushState.my_sub == None,  # noqa: E711
        rx.cond(
            rx.State.is_hydrated & ~PushState.waiting_for_registration,
            rx.button(
                "Register for push notifications",
                on_click=[
                    trigger_register(PushState.browser_id),
                    PushState.set_waiting_for_registration(True),
                ],
            ),
            rx.spinner(),
        ),
        rx.hstack(
            rx.text(f"Registered as {PushState.my_sub.auth_key}"),
            rx.switch(
                checked=PushState.my_sub.enabled, on_change=PushState.set_sub_status
            ),
        ),
    )


def notification_form(on_submit):
    return rx.form(
        rx.table.root(
            rx.table.row(
                rx.table.cell(rx.text("Title")),
                rx.table.cell(rx.input(name="title")),
            ),
            rx.table.row(
                rx.table.cell(rx.text("Body")),
                rx.table.cell(rx.input(name="body")),
            ),
            rx.table.row(
                rx.table.cell(rx.text("Icon (url)")),
                rx.table.cell(rx.input(name="icon")),
            ),
            rx.table.row(
                rx.table.cell(rx.text("URL")),
                rx.table.cell(rx.input(name="url")),
            ),
            rx.button("Push"),
        ),
        reset_on_submit=True,
        on_submit=on_submit,
    )


def other_subscriber_list() -> rx.Component:
    return rx.fragment(
        rx.hstack(
            rx.heading("Other Subscribers"),
            rx.icon_button(
                "refresh-cw",
                disabled=PushState.refreshing,
                on_click=PushState.refresh,
            ),
        ),
        rx.unordered_list(
            rx.foreach(
                PushState.other_subs,
                lambda sub: rx.list_item(
                    rx.hstack(
                        rx.text(sub.auth_key),
                        rx.cond(sub.enabled, rx.icon("check")),
                    ),
                ),
            ),
        ),
    )


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.script(src="/push.js"),
        rx.moment(
            interval=rx.cond(PushState.waiting_for_registration, 1000, 0),
            on_change=PushState.refresh,
            display="none",
        ),
        rx.vstack(
            rx.heading("Welcome to Push Notification Tester!", size="9"),
            registration_status(),
            rx.cond(
                PushState.my_sub != None,  # noqa: E711
                notification_form(PushState.do_push_all),
            ),
            other_subscriber_list(),
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index, on_load=PushState.refresh)
add_register_push_endpoint(app)

# create db on hosting service
rx.Model.migrate()
