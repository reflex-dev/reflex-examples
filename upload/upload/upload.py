import asyncio
import os
from typing import List

import pynecone as pc


class State(pc.State):
    """The app state."""

    # Whether we are currently uploading files.
    is_uploading: bool

    @pc.var
    def file_str(self) -> str:
        """Get the string representation of the uploaded files."""
        return "\n".join(os.listdir(pc.get_asset_path()))

    async def handle_upload(self, files: List[pc.UploadFile]):
        """Handle the file upload."""
        self.is_uploading = True

        # Iterate through the uploaded files.
        for file in files:
            upload_data = await file.read()
            outfile = pc.get_asset_path(file.filename)
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
    return pc.vstack(
        pc.upload(
            pc.button(
                "Select File(s)",
                height="70px",
                width="200px",
                color=color,
                bg="white",
                border=f"1px solid {color}",
            ),
            pc.text(
                "Drag and drop files here or click to select files",
                height="100px",
                width="200px",
            ),
            border="1px dotted black",
            padding="2em",
        ),
        pc.hstack(
            pc.button(
                "Upload",
                on_click=State.handle_upload(pc.upload_files()),
            ),
        ),
        pc.heading("Files:"),
        pc.cond(
            State.is_uploading,
            pc.progress(is_indeterminate=True, color="blue", width="100%"),
            pc.progress(value=0, width="100%"),
        ),
        pc.text_area(
            is_disabled=True,
            value=State.file_str,
            width="100%",
            height="100%",
            bg="white",
            color="black",
            placeholder="No File",
            min_height="20em",
        ),
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Upload")
app.compile()
