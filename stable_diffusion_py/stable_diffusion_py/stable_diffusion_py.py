"""Welcome to Pynecone! This file outlines the steps to create a basic Stable Diffusion app."""
import pynecone as pc
from typing import List
from PIL import Image
import platform

from stable_diffusion_py.styles import *

# Check if the operating system is Linux or macOS
os_name = platform.system()
if os_name == "Linux":
    from stable_diffusion_py.img2img_linux import img2img
elif os_name == "Darwin":
    from stable_diffusion_py.img2img_mac import img2img
else:
    raise OSError("Unsupported operating system: " + os_name)


class State(pc.State):
    """The app state."""

    prompt = ""
    negative_prompt = ""
    # Takes the final upload from img variable
    most_recent_upload = ""
    strength_diffusion = 70
    image_processing = False
    image_made = False
    # Uploaded images.
    img: list[str]
    inference_steps = 100
    image = Image.open("assets/favicon.ico")

    def process_image(self):
        """Set the image processing flag to true and indicate that the image has not been made yet."""
        self.image_made = False
        self.image_processing = True

    async def handle_upload(self, files: List[pc.UploadFile]):
        """Handle the upload of file(s).

        Args:
            files: The uploaded files.
        """
        for file in files:
            upload_data = await file.read()
            outfile = f".web/public/{file.filename}"

            # Save the file.
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)

            # Update the img var.
            self.img.append(file.filename)
            print(self.img)
            self.most_recent_upload = self.img[-1]

    def stable_diffusion(self):
        image = self.img[-1]
        image = f".web/public/{image}"
        image = Image.open(image)
        rgb_image = image.convert("RGB")
        print(self.prompt)
        sd_image = img2img(
            img=rgb_image,
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            strength=(self.strength_diffusion / 100),
            guidance_scale=8.5,
            num_inference_steps=self.inference_steps,
            seed=100,
        )

        self.image_processing = False
        self.image_made = True
        self.image = sd_image


def index():
    """The main view."""
    return pc.center(
        pc.vstack(
            pc.heading("Stable Diffusion", font_size="2em"),
            pc.upload(
                pc.vstack(
                    pc.button(
                        pc.text("Select File"),
                        _hover={"bg": accent_color},
                        style=input_style,
                    ),
                    pc.text("Drag and drop files here or click to select files"),
                ),
                border=f"1px dotted blue",
                padding="5em",
            ),
            pc.button(
                pc.text("Upload"),
                _hover={"bg": accent_color},
                style=input_style,
                on_click=lambda: State.handle_upload(pc.upload_files()),
            ),
            pc.image(src=State.most_recent_upload, style=image_style),
            pc.vstack(
                pc.input(
                    placeholder="Enter a prompt..",
                    on_change=State.set_prompt,
                    _placeholder={"color": "#fffa"},
                    _hover={"border_color": accent_color},
                    style=input_style,
                ),
                pc.input(
                    placeholder="Enter a negative prompt..",
                    on_change=State.set_negative_prompt,
                    _placeholder={"color": "#fffa"},
                    _hover={"border_color": accent_color},
                    style=input_style,
                ),
                pc.text("Number of inference steps: " + State.inference_steps),
                pc.slider(
                    on_change_end=State.set_inference_steps,
                    color_scheme="green",
                    default_value=100,
                    min_=3,
                    max_=200,
                ),
                pc.text("Strength of diffusion: " + State.strength_diffusion),
                pc.slider(
                    on_change_end=State.set_strength_diffusion,
                    color_scheme="green",
                    default_value=70,
                    min_=0,
                    max_=100,
                ),
                pc.button(
                    pc.text("Generate New Image"),
                    _hover={"bg": accent_color},
                    style=input_style,
                    on_click=[State.process_image, State.stable_diffusion],
                    width="100%",
                ),
                pc.divider(),
                pc.cond(
                    State.image_processing,
                    pc.circular_progress(is_indeterminate=True),
                    pc.cond(
                        State.image_made,
                        pc.image(src=State.image, style=image_style),
                    ),
                ),
            ),
            bg=border_color,
            padding="2em",
            shadow="shadow_light",
            border_radius="lg",
        ),
        width="100%",
        min_h="100vh",
        bg=bg_dark_color,
        color=text_light_color,
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Pynecone: Stable Diffusion")
app.compile()
