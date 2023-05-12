import os
import pynecone as pc
from typing import List
class State(pc.State):
    """The app state."""
    files_path:str = f".web/public/files/"
    str_files:str=""
    async def handle_upload(self, files: List[pc.UploadFile]):
        if(False is os.path.exists(self.files_path)):
            os.makedirs(self.files_path, 0o755)
        for file in files:
            upload_data = await file.read()
            output_filepath = self.files_path + file.filename
            with open(output_filepath, "wb") as file_object:
                file_object.write(upload_data)
        filelist = os.listdir(self.files_path)
        self.str_files = ""
        for filename in filelist:
            self.str_files = self.str_files+filename+"\n"

def index():
    return pc.vstack(
        pc.hstack(
            pc.button(
                "Upload", 
                on_click=lambda: State.handle_upload(pc.upload_files())
            ),
        ),
        pc.upload(
            pc.button("Select File", height="70px", width="200px"),
            pc.text("Drag and drop files here or click to select files", height="100px", width="200px"),
            border="1px dotted black",
            padding="2em",
        ),
        pc.text_area(
            is_disabled=True,
            value=State.str_files,
            width="100%",
            height="100%",
            bg="white",
            color="black",
            placeholder="Response",
            min_height="20em",
        ),
    )

# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Upload")
app.compile()