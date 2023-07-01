"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
import openai

openai.api_key = "YOUR_API_KEY"


class State(pc.State):
    """The app state."""
    image_url = ""
    image_processing = False
    image_made = False
    def get_dalle_result(self, form_data: dict[str, str]):
        prompt_text:str = form_data["prompt_text"]
        self.image_made = False
        self.image_processing = True
        yield
        try:
            response = openai.Image.create(prompt=prompt_text, n=1, size="1024x1024")
            self.image_url = response["data"][0]["url"]
            self.image_processing = False
            self.image_made = True
            yield
        except:
            self.image_processing = False
            yield pc.window_alert("Error with OpenAI Execution.")

def index():
    return pc.center(
        pc.vstack(
            pc.heading("DALL-E", font_size="1.5em"),
            pc.form(
                pc.input(id="prompt_text", placeholder="Enter a prompt.."),
                pc.button(
                    "Generate Image",
                    type_="submit",
                    width="100%",
                ),
                on_submit=State.get_dalle_result,
            ),
            pc.divider(),
            pc.cond(
                State.image_processing,
                pc.circular_progress(is_indeterminate=True),
                pc.cond(
                    State.image_made,
                    pc.image(
                        src=State.image_url,
                        height="25em",
                        width="25em",
                    ),
                ),
            ),
            bg="white",
            padding="2em",
            shadow="lg",
            border_radius="lg",
        ),
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )

# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Pynecone:DALL-E")
app.compile()
