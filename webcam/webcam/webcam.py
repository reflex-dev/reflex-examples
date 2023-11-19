"""This example reuses the existing file upload functionality to upload webcam data."""
import inspect
import time
from pathlib import Path
from urllib.request import urlopen

from PIL import Image

import reflex as rx
from reflex.components.media import image


class State(rx.State):
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: str = ""
    auto_screenshot_period: int = 0

    async def handle_screenshot(self, img_data_uri: str):
        """Webcam screenshot upload handler."""
        with urlopen(img_data_uri) as img:
            self.last_screenshot = Image.open(img)
            self.last_screenshot.load()
            self.last_screenshot.format = "WEBP"  # convert to webp for smaller size
        self.last_screenshot_timestamp = time.strftime("%H:%M:%S")

    def set_auto_screenshot_period(self, period: int):
        """Set the auto screenshot period."""
        self.auto_screenshot_period = int(period)


class Webcam(rx.Component):
    """Wrapper for react-webcam component."""

    library = "react-webcam"
    tag = "Webcam"
    is_default = True

    screenshot_format: rx.Var[str] = "image/jpeg"


def upload_screenshot(ref, handler):
    """Helper to capture and upload a screenshot from a webcam component.

    Args:
        ref: The ref of the webcam component.
        handler: The event handler that receives the screenshot.
    """
    return rx.call_script(
        f"refs['ref_{ref}'].current.getScreenshot()",
        callback=handler,
    )


def auto_screenshot_widget(ref: str):
    return rx.vstack(
        rx.form_label(
            f"Auto Screenshot Period ({State.auto_screenshot_period}ms)",
            rx.slider(
                value=State.auto_screenshot_period,
                on_change=State.set_auto_screenshot_period,
                min_=0, max_=10000, step=200,
            ),
        ),
        # Take a new screenshot automatically
        rx.box(
            rx.moment(
                interval=State.auto_screenshot_period,
                on_change=upload_screenshot("webcam", State.handle_screenshot),
            ),
            display="none",
        ),
    )


def webcam_upload_component():
    return rx.vstack(
        Webcam.create(
            id="webcam",
            on_click=upload_screenshot(
                ref="webcam",
                handler=State.handle_screenshot,
            ),
        ),
        rx.cond(
            State.last_screenshot,
            rx.fragment(
                rx.image(src=State.last_screenshot),
                rx.text(State.last_screenshot_timestamp),
            ),
            rx.center("Click to capture image."),
        ),
        auto_screenshot_widget("webcam"),
        width="320px",
        height="600px",
    )


def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.center(
            webcam_upload_component(),
        ),
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
