
import google.generativeai as genai

import reflex as rx

_model = None


def get_gemini_client():

    GOOGLE_API_KEY = 'AIzaSyCExrlmk6O9YjnicvR746Xfm3jhg7N8KO0'
    genai.configure(api_key=GOOGLE_API_KEY)
    global _model
    if _model is None:
        _model = genai.GenerativeModel('gemini-pro')

    return _model


class State(rx.State):
    """The app state."""

    answer_processing = False
    answer_made = False
    answer = ""

    def get_dalle_result(self, form_data: dict[str, str]):
        prompt_text: str = form_data["prompt_text"]
        self.answer_made = False
        self.answer_processing = True
        # Yield here so the image_processing take effects and the circular progress is shown.
        yield
        try:
            response = get_gemini_client().generate_content(prompt_text)
            # self.image_url = response.data[0].url
            self.answer_processing = False
            self.answer_made = True
            self.answer = response.text
            print(response)
            yield
        except Exception as ex:
            self.answer_processing = False
            yield rx.window_alert(f"Error with Gemini Execution. {ex}")
