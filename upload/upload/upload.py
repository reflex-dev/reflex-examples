import os
import asyncio
import pynecone as pc
from typing import List

class State(pc.State):
    """The app state."""
    files_path:str = f".web/public/files/"
    str_files:str=""
    is_uploading:bool=False
    async def handle_upload(self, files: List[pc.UploadFile]):
        self.is_uploading = True
        if(False is os.path.exists(self.files_path)):
            os.makedirs(self.files_path, 0o755)
        for file in files:
            upload_data = await file.read()
            output_filepath = self.files_path + file.filename
            with open(output_filepath, "wb") as file_object:
                file_object.write(upload_data)
        return self.show_files
    
    async def show_files(self):
        await asyncio.sleep(1.0)
        self.is_uploading = False
        if(False is os.path.exists(self.files_path)):
            os.makedirs(self.files_path, 0o755)
        filelist = os.listdir(self.files_path)
        self.str_files = ""
        for filename in filelist:
            self.str_files = self.str_files+filename+"\n"

color = "rgb(107,99,246)"
def index():
    return pc.vstack(
        pc.upload(
            #pc.button("Select File", ),
            pc.button(
                "Select File(s)",
                height="70px",
                width="200px",
                color=color,
                bg="white",
                border=f"1px solid {color}",
            ),
            pc.text("Drag and drop files here or click to select files", height="100px", width="200px"),
            border="1px dotted black",
            padding="2em",
        ),
        pc.hstack(
            pc.button(
                "Upload", 
                on_click=State.handle_upload(pc.upload_files()),
            ),
            pc.button(
                "Refresh", 
                on_click=State.show_files,
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
            value=State.str_files,
            width="100%",
            height="100%",
            bg="white",
            color="black",
            placeholder="No File",
            min_height="20em",
        ),
    )

# Add state and page to the app.
app = pc.App(state=State, on_load=State.show_files())
app.add_page(index, title="Upload")
app.compile()