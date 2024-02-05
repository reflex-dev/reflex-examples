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

    @rx.var
    def is_link(self) -> bool:
        return self.last_scan.startswith("http")


def index() -> rx.Component:
    return rx.chakra.vstack(
        rx.chakra.heading("@yudiel/react-qr-scanner", font_size="2em"),
        rx.chakra.box(
            rx.cond(
                State.last_error,
                rx.chakra.text("Error: ", State.last_error),
            ),
        ),
        rx.chakra.box(
            qr_scanner(
                on_decode=State.on_decode,
                on_result=State.on_result,
                on_error=State.on_error,
                container_style={
                    "width": "32vh",
                    "height": "24vh",
                    "paddingTop": "0",
                },
            ),
        ),
        rx.chakra.center(
            rx.cond(
                State.last_scan,
                rx.cond(
                    State.is_link,
                    rx.chakra.link(State.last_scan, href=State.last_scan),
                    rx.chakra.text(State.last_scan),
                ),
                rx.chakra.text("Scan a valid QR code"),
            ),
            border="1px solid black",
            width="80vw",
        ),
        rx.chakra.code(State.json_result, white_space="pre-wrap"),
        spacing="1.5em",
    )


app = rx.App()
app.add_page(index)
