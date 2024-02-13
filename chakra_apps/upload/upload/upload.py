import os
from typing import List

import reflex as rx


class State(rx.State):
    """The app state."""

    # Whether we are currently uploading files.
    is_uploading: bool

    # Progress visuals
    upload_progress: int

    @rx.var
    def files(self) -> list[str]:
        """Get the string representation of the uploaded files."""
        return os.listdir(rx.get_upload_dir())

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Handle the file upload."""
        # Iterate through the uploaded files.
        for file in files:
            upload_data = await file.read()
            outfile = os.path.join(rx.get_upload_dir(), file.filename)
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)

    def on_upload_progress(self, prog: dict):
        print("Got progress", prog)
        if prog["progress"] < 1:
            self.is_uploading = True
        else:
            self.is_uploading = False
        self.upload_progress = round(prog["progress"] * 100)


color = "rgb(107,99,246)"


def index():
    return rx.vstack(
        rx.upload(
            rx.button(
                "Select File(s)",
                height="70px",
                width="200px",
                color=color,
                bg="white",
                border=f"1px solid {color}",
            ),
            rx.text(
                "Drag and drop files here or click to select files",
                height="100px",
                width="200px",
            ),
            border="1px dotted black",
            padding="2em",
        ),
        rx.hstack(
            rx.button(
                "Upload",
                on_click=State.handle_upload(rx.upload_files(on_upload_progress=State.on_upload_progress)),
            ),
        ),
        rx.heading("Files:"),

        rx.cond(
            State.is_uploading,
            rx.progress(value=State.upload_progress),
            rx.progress(value=0),
        ),
        rx.vstack(
           rx.foreach(State.files, lambda file: rx.link(file, href=rx.get_upload_url(file)))
        ),
    )


app = rx.App()
app.add_page(index, title="Upload")
