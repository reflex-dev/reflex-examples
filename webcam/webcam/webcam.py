"""This example reuses the existing file upload functionality to upload webcam data."""
import inspect
import time
from pathlib import Path
from urllib.request import urlopen

from PIL import Image

import reflex as rx


class State(rx.State):
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: str = ""

    upload_progress: dict[str, int | str] = {
        "loaded": 0,
        "total": 0,
        "progress": "100%",
    }

    async def handle_screenshot(self, files: list[rx.UploadFile]):
        """Webcam screenshot upload handler."""
        print("Handling screenshot!")
        for f in files:
            img_data_uri = await f.read()
            with urlopen(img_data_uri.decode()) as img:
                self.last_screenshot = Image.open(img)
                self.last_screenshot.load()
                print(f"Uploaded image: {self.last_screenshot}")
        self.last_screenshot_timestamp = time.strftime("%H:%M:%S")

    def cb(self, res):
        """Callback for upload completion."""
        print("Upload complete!")

    def on_progress(self, prog):
        """Callback for upload progress."""
        self.upload_progress["loaded"] = prog["loaded"]
        self.upload_progress["total"] = prog["total"]
        self.upload_progress["progress"] = f"{round(prog.get('progress', 0) * 100)}%"


def format_on_progress(on_progress: rx.event.EventHandler) -> str:
    """Format an on_progress event handler for upload_data."""
    args_spec = rx.upload_files.on_upload_progress_args_spec
    params = ", ".join(f"_{p}" for p in inspect.signature(args_spec).parameters)
    on_progress_event = rx.utils.format.format_event(
        rx.event.call_event_handler(on_progress, args_spec),
    )
    return f"({params}) => queueEvents([{on_progress_event}], socket)"


def upload_data(
    data: str,
    handler: rx.event.EventHandler,
    on_progress: rx.event.EventHandler | None = None,
    on_complete: rx.event.EventHandler | None = None,
) -> rx.event.EventSpec:
    """Upload data to the server via a file upload handler.

    Args:
        data: The data to upload (anything Blob-able).
        handler: The file upload handler to use.
        on_progress: An optional event handler to call with upload progress.
        on_complete: An optional event handler to call when the upload is complete.

    Returns:
        An event spec that initiates the upload.
    """
    handler_str = ".".join(rx.utils.format.get_event_handler_parts(handler))
    on_progress_str = (
        format_on_progress(on_progress) if on_progress is not None else "undefined"
    )
    return rx.call_script(
        f"uploadFiles({handler_str!r}, [new Blob([{data}])], {handler_str!r}, {on_progress_str}, socket)",
        callback=on_complete,
    )


class Webcam(rx.Component):
    """Wrapper for react-webcam component."""

    library = "react-webcam"
    tag = "Webcam"
    is_default = True

    screenshot_format: rx.Var[str] = "image/jpeg"


def upload_screenshot(ref, handler, on_progress=None, on_complete=None):
    """Helper to capture and upload a screenshot from a webcam component.

    Args:
        ref: The ref of the webcam component.
        handler: The file upload handler to use.
        on_progress: An optional event handler to call with upload progress.
        on_complete: An optional event handler to call when the upload is complete.
    """
    return upload_data(
        data=f"refs['ref_{ref}'].current.getScreenshot()",
        handler=handler,
        on_progress=on_progress,
        on_complete=on_complete,
    )


def webcam_upload_component():
    return rx.vstack(
        Webcam.create(
            id="webcam",
            on_click=upload_screenshot(
                ref="webcam",
                handler=State.handle_screenshot,
                on_progress=State.on_progress,
                on_complete=State.cb,
            ),
        ),
        rx.text(f"Upload Progress: {State.upload_progress['progress']}"),
        rx.progress(
            value=State.upload_progress["loaded"].to(int),
            max_=State.upload_progress["total"].to(int),
            width="100%",
        ),
        rx.cond(
            State.last_screenshot,
            rx.fragment(
                rx.image(src=State.last_screenshot),
                rx.text(State.last_screenshot_timestamp),
            ),
            rx.center("Click to capture image."),
        ),
        width="320px",
        height="600px",
    )


def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.center(webcam_upload_component()),
        rx.vstack(
            rx.heading("Source Code"),
            rx.code_block(
                Path(__file__).read_text(),
                language="python",
                width="90%",
                overflow_x="auto",
            ),
        ),
    )


app = rx.App()
app.add_page(
    index,
    title="Upload Webcam Demo",
    description="An example of uploading webcam data via REST.",
)
app.compile()
