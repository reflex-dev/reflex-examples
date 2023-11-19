"""Wrapper for react-webcam component."""
import reflex as rx


class Webcam(rx.Component):
    """Wrapper for react-webcam component."""

    library = "react-webcam"
    tag = "Webcam"
    is_default = True

    screenshot_format: rx.Var[str] = "image/jpeg"  # type: ignore


webcam = Webcam.create


def upload_screenshot(ref: str, handler: rx.event.EventHandler):
    """Helper to capture and upload a screenshot from a webcam component.

    Args:
        ref: The ref of the webcam component.
        handler: The event handler that receives the screenshot.
    """
    return rx.call_script(
        f"refs['ref_{ref}'].current.getScreenshot()",
        callback=handler,
    )
