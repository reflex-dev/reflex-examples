"""Wrapper for react-webcam component."""
import reflex as rx


class Webcam(rx.Component):
    """Wrapper for react-webcam component."""

    library = "react-webcam"
    tag = "Webcam"
    is_default = True

    screenshot_format: rx.Var[str] = "image/jpeg"  # type: ignore

    def _get_hooks(self) -> str | None:
        if self.id is not None:
            return (super()._get_hooks() or "") + f"refs['mediarecorder_{self.id}'] = useRef(null)"
        return super()._get_hooks()


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


def start_recording(
    ref: str,
    on_data_available: rx.event.EventHandler,
    on_start: rx.event.EventHandler = None,
    on_stop: rx.event.EventHandler = None,
    timeslice: str = "",
) -> str:
    """Helper to start recording a video from a webcam component.

    Args:
        ref: The ref of the webcam component.
        handler: The event handler that receives the video chunk by chunk.
        timeslice: How often to emit a chunk. Defaults to "" which means only at the end.

    Returns:
        The ref of the media recorder to stop recording.
    """
    on_data_available_event = rx.utils.format.format_event(
        rx.event.call_event_handler(on_data_available, arg_spec=lambda data: [data])
    )
    if on_start is not None:
        on_start_event = rx.utils.format.format_event(
            rx.event.call_event_handler(on_start, arg_spec=lambda e: [])
        )
        on_start_callback = f"mediaRecorderRef.current.addEventListener('start', () => applyEvent({on_start_event}, socket))"
    else:
        on_start_callback = ""

    if on_stop is not None:
        on_stop_event = rx.utils.format.format_event(
            rx.event.call_event_handler(on_stop, arg_spec=lambda e: [])
        )
        on_stop_callback = f"mediaRecorderRef.current.addEventListener('stop', () => applyEvent({on_stop_event}, socket))"
    else:
        on_stop_callback = ""

    return rx.call_script(
        f"""
        const handleDataAvailable = (e) => {{
            if (e.data.size > 0) {{
                var a = new FileReader();
                a.onload = (e) => {{
                    const _data = e.target.result
                    applyEvent({on_data_available_event}, socket)
                }}
                a.readAsDataURL(e.data);
            }}
        }}
        const mediaRecorderRef = refs['mediarecorder_{ref}']
        if (mediaRecorderRef.current != null) {{
            mediaRecorderRef.current.stop()
        }}
        mediaRecorderRef.current = new MediaRecorder(refs['ref_{ref}'].current.stream, {{mimeType: 'video/webm'}})
        mediaRecorderRef.current.addEventListener(
          "dataavailable",
          handleDataAvailable,
        );
        {on_start_callback}
        {on_stop_callback}
        mediaRecorderRef.current.start({timeslice})""",
    )


def stop_recording(ref: str):
    """Helper to stop recording a video from a webcam component.

    Args:
        ref: The ref of the webcam component.
        handler: The event handler that receives the video blob.
    """
    return rx.call_script(
        f"refs['mediarecorder_{ref}'].current.stop()",
    )