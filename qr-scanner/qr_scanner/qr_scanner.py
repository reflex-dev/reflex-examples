import json
from typing import Any

import reflex as rx

from .component import qr_scanner


class State(rx.State):
    last_scan: str = ""
    last_result: dict[str, Any] = {}
    last_error: str = ""

    def on_decode(self, decoded: str):
        if decoded:
            self.last_scan = decoded

    def on_result(self, result: dict[str, Any]):
        if result:
            self.last_error = ""
            self.last_result = result

    def on_error(self, error: str):
        self.last_error = error

    @rx.var
    def json_result(self) -> str:
        return json.dumps(self.last_result, indent=2)


def index() -> rx.Component:
    return rx.vstack(
        rx.heading("@yudiel/react-qr-scanner", font_size="2em"),
        rx.box(
            rx.cond(
                State.last_scan,
                rx.text(State.last_scan),
                rx.text("Scan a valid QR code"),
            ),
        ),
        rx.box(
            rx.cond(
                State.last_error,
                rx.text("Error: ", State.last_error),
            ),
        ),
        rx.hstack(
            rx.code(State.json_result, width="40vw", white_space="pre-wrap"),
            qr_scanner(
                on_decode=State.on_decode,
                on_result=State.on_result,
                on_error=State.on_error,
                container_style={
                    "width": "640px",
                    "height": "480px",
                    "paddingTop": "0",
                },
            ),
            align_items="top",
        ),
        spacing="1.5em",
    )


app = rx.App()
app.add_page(index)
app.compile()