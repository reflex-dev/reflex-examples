"""Take screenshots from webcam and perform object detection using tensorflow hub model."""
import time
from pathlib import Path
from urllib.request import urlopen

from PIL import Image

import reflex as rx
from reflex.components.media import image

from . import object_detection, react_webcam


# Identifies a particular webcam component in the DOM
WEBCAM_REF = "webcam"

# The path containing the app
APP_PATH = Path(__file__)
APP_MODULE_DIR = APP_PATH.parent
SOURCE_CODE = [
    APP_MODULE_DIR / "react_webcam.py",
    APP_PATH,
    APP_MODULE_DIR / "object_detection.py",
    APP_MODULE_DIR.parent / "requirements.txt",
]


class State(rx.State):
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: str = ""
    auto_screenshot_period: int = 0
    detect_objects: bool = False
    loading: bool = False
    recording: bool = False
    video_files: int = 0

    def handle_screenshot(self, img_data_uri: str):
        """Webcam screenshot upload handler.

        Args:
            img_data_uri: The data uri of the screenshot (from upload_screenshot).
        """
        if self.loading:
            return
        self.last_screenshot_timestamp = time.strftime("%H:%M:%S")
        with urlopen(img_data_uri) as img:
            self.last_screenshot = Image.open(img)
            self.last_screenshot.load()
            # convert to webp during serialization for smaller size
            self.last_screenshot.format = "WEBP"  # type: ignore
            if self.detect_objects:
                yield State.run_detector

    @rx.background
    async def run_detector(self):
        """Run object detection on the last screenshot."""
        async with self:
            if self.loading or self.last_screenshot is None:
                return
            self.loading = True
        try:
            image_with_boxes = await object_detection.run_detector_async(
                self.last_screenshot
            )
            async with self:
                self.last_screenshot = image_with_boxes
        finally:
            async with self:
                self.loading = False

    def set_auto_screenshot_period(self, period: int):
        """Set the auto screenshot period."""
        self.auto_screenshot_period = int(period)

    @rx.cached_var
    def video_path(self) -> str:
        return f"assets/video_{self.video_files}.webm"

    def on_start_recording(self):
        self.recording = True
        self.video_files += 1
        print("Started recording")
        with open(self.video_path, "wb") as f:
            f.write(b"")

    def handle_video_chunk(self, chunk: str):
        print("Got video chunk", len(chunk))
        with open(self.video_path, "ab") as f:
            with urlopen(chunk.replace("codecs=avc1,opus;", "")) as vid:
                f.write(vid.read())

    def on_stop_recording(self):
        print(f"Stopped recording: {self.video_path}")
        self.recording = False

    def start_recording(self, ref: str):
        """Start recording a video."""
        return react_webcam.start_recording(
            ref,
            on_data_available=State.handle_video_chunk,
            on_start=State.on_start_recording,
            on_stop=State.on_stop_recording,
            timeslice=1000,
        )


def auto_screenshot_widget(ref: str) -> rx.Component:
    """Widget for configuring auto screenshot period.

    Args:
        ref: The ref of the webcam component to screenshot.

    Returns:
        A reflex component.
    """
    return rx.vstack(
        rx.form_label(
            f"Auto Screenshot Period ({State.auto_screenshot_period}ms)",
            rx.slider(
                value=State.auto_screenshot_period,
                on_change=State.set_auto_screenshot_period,
                min_=0,
                max_=10000,
                step=200,
            ),
        ),
        # Take a new screenshot automatically
        rx.box(
            rx.moment(
                interval=State.auto_screenshot_period,
                on_change=react_webcam.upload_screenshot(
                    ref=ref,
                    handler=State.handle_screenshot,  # type: ignore
                ),
            ),
            display="none",
        ),
    )


def detect_objects_widget() -> rx.Component:
    """Widget for toggling object detection and showing progress."""
    return rx.fragment(
        rx.cond(State.loading, rx.progress(is_indeterminate=True, width="100%")),
        rx.form_label(
            rx.span("Detect Objects", margin_right="1em"),
            rx.switch(
                is_checked=State.detect_objects,
                on_change=State.set_detect_objects,  # type: ignore
            ),
        ),
    )


def last_screenshot_widget() -> rx.Component:
    """Widget for displaying the last screenshot and timestamp."""
    return rx.box(
        rx.cond(
            State.last_screenshot,
            rx.fragment(
                rx.image(src=State.last_screenshot),
                rx.text(State.last_screenshot_timestamp),
            ),
            rx.center("Click to capture image."),
        ),
        height="270px",
    )


def webcam_upload_component(ref: str) -> rx.Component:
    """Component for displaying webcam preview and uploading screenshots.

    Args:
        ref: The ref of the webcam component.

    Returns:
        A reflex component.
    """
    return rx.vstack(
        react_webcam.webcam(
            id=ref,
            on_click=react_webcam.upload_screenshot(
                ref=ref,
                handler=State.handle_screenshot,  # type: ignore
            ),
            audio=True,
        ),
        rx.cond(
            ~State.recording,
            rx.button("🟢 Start Recording", on_click=State.start_recording(ref), color_scheme="green"),
            rx.button("🟤 Stop Recording", on_click=react_webcam.stop_recording(ref), color_scheme="red"),
        ),
        last_screenshot_widget(),
        rx.vstack(
            detect_objects_widget(),
            auto_screenshot_widget(ref),
        ),
        width="320px",
    )


def color_mode_code_block(code: str, **kwargs: str) -> rx.Component:
    """Code block theme depends on color mode."""
    return rx.color_mode_cond(
        light=rx.code_block(
            code,
            theme="light",
            **kwargs,  # type: ignore
        ),
        dark=rx.code_block(
            code,
            theme="dark",
            **kwargs,  # type: ignore
        ),
    )


@rx.page(
    title="Upload Webcam Demo",
    description="An example of uploading and processing webcam data.",
)
def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.center(
            webcam_upload_component(WEBCAM_REF),
            padding_top="3em",
        ),
        *[
            rx.vstack(
                rx.heading(f"Source Code: {p.name}"),
                color_mode_code_block(
                    p.read_text(),
                    language="python",
                    width="90%",
                    overflow_x="auto",
                ),
            )
            for p in SOURCE_CODE
        ],
    )


app = rx.App()
app.compile()
