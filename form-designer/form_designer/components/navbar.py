import reflex as rx

import reflex_local_auth
from reflex_local_auth import LocalAuthState


def navbar_menu() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(rx.icon("menu", size=20), cursor="pointer"),
        rx.menu.content(
            rx.cond(
                LocalAuthState.is_authenticated,
                rx.fragment(
                    rx.hstack(
                        rx.avatar(
                            fallback=LocalAuthState.authenticated_user.username[0],
                            size="1",
                        ),
                        rx.text(
                            LocalAuthState.authenticated_user.username,
                        ),
                        margin="8px",
                    ),
                    rx.menu.separator(),
                ),
            ),
            rx.menu.item("Home", on_click=rx.redirect("/")),
            rx.cond(
                LocalAuthState.is_authenticated,
                rx.menu.item(
                    "Logout",
                    on_click=[
                        LocalAuthState.do_logout,
                        rx.redirect("/"),
                    ],
                ),
                rx.fragment(
                    rx.menu.item(
                        "Register",
                        on_click=rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE),
                    ),
                    rx.menu.item(
                        "Login",
                        on_click=rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE),
                    ),
                ),
            ),
            rx.menu.separator(),
            rx.hstack(
                rx.icon("sun", size=16),
                rx.color_mode.switch(size="1"),
                rx.icon("moon", size=16),
                margin="8px",
            ),
        ),
    )


def navbar() -> rx.Component:
    return rx.hstack(
        rx.heading("Form Designer"),
        rx.spacer(),
        navbar_menu(),
        margin_y="12px",
        align="center",
    )
