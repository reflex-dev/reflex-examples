from typing import Dict
import reflex as rx
from reflex.components.component import NoSSRComponent
from reflex.vars import BaseVar, Var


class QrScanner(NoSSRComponent):
    library = "@yudiel/react-qr-scanner"
    tag = "QrScanner"

    # The delay between scans in milliseconds.
    scan_delay: rx.Var[int]

    # The id of the element to disaply the video preview
    video_id: rx.Var[str]

    # Whether to display the scan count overlay on the video.
    hide_count: rx.Var[bool]

    container_style: rx.Var[Dict[str, str]]
    video_style: rx.Var[Dict[str, str]]

    def get_controlled_triggers(self) -> Dict[str, Var]:
        """Dict mapping (event -> expected arguments)."""
        return super().get_controlled_triggers() | {
            "on_result": rx.EVENT_ARG,
            "on_decode": rx.EVENT_ARG,
            "on_error": BaseVar(name=rx.EVENT_ARG.name + "?.message", type_=str),
        }

qr_scanner = QrScanner.create