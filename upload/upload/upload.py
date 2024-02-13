import asyncio
import os
from typing import List

import reflex as rx


class State(rx.State):
    """The app state."""

    # Whether we are currently uploading files.
    is_uploading: bool

    @rx.var
    def files(self) -> list[str]:
        """Get the string representation of the uploaded files."""
        return os.listdir(rx.get_upload_dir())

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Handle the file upload."""
        self.is_uploading = True

        # Iterate through the uploaded files.
        for file in files:
            upload_data = await file.read()
            outfile = os.path.join(rx.get_upload_dir(), file.filename)
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)

        # Stop the upload.
        return State.stop_upload

    async def stop_upload(self):
        """Stop the file upload."""
        await asyncio.sleep(1)
        self.is_uploading = False


color = "rgb(107,99,246)"


def index():
    return rx.chakra.vstack(
        rx.upload(
            rx.chakra.button(
                "Select File(s)",
                height="70px",
                width="200px",
                color=color,
                bg="white",
                border=f"1px solid {color}",
            ),
            rx.chakra.text(
                "Drag and drop files here or click to select files",
                height="100px",
                width="200px",
            ),
            border="1px dotted black",
            padding="2em",
        ),
        rx.chakra.hstack(
            rx.chakra.button(
                "Upload",
                on_click=State.handle_upload(rx.upload_files()),
            ),
        ),
        rx.chakra.heading("Files:"),
        rx.cond(
            State.is_uploading,
            rx.chakra.progress(is_indeterminate=True, color="blue", width="100%"),
            rx.chakra.progress(value=0, width="100%"),
        ),
        rx.chakra.vstack(
           rx.foreach(State.files, lambda file: rx.link(file, href=rx.get_upload_url(file)))
        ),
    )


app = rx.App()
app.add_page(index, title="Upload")
