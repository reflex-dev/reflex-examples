from .base import Base
import reflex as rx

from io import BytesIO
from docx import Document


class DocumentState(Base):

    counter: int = 0
    content: list[list[str]]
    filename: str

    upload_ui: str = "flex"
    document_ui: str = "none"

    first_word_id: int
    last_word_id: int

    async def get_document(self, files: list[rx.UploadFile]):
        self.upload_ui, self.document_ui = "none", "flex"

        for file in files:
            upload_data = await file.read()

            file_stream = BytesIO(upload_data)

            try:
                doc = Document(file_stream)

                for paragraph in doc.paragraphs:
                    words = paragraph.text.split()

                    for word in words:
                        self.content.append([word, self.counter, "transparent"])
                        self.counter += 1

            except Exception:
                self.upload_ui, self.document_ui = "flex", "none"
                return rx.toast.error("Upload was not successful.")

    def highlight_start(self, word_id):
        self.first_word_id = word_id

    def highlight_end(self, word_id):
        self.last_word_id = word_id
        self.process_highlight()

    def process_highlight(self):

        start_index = next(
            (
                index
                for index, word in enumerate(self.content)
                if word[1] == self.first_word_id
            ),
            None,
        )
        end_index = next(
            (
                index
                for index, word in enumerate(self.content)
                if word[1] == self.last_word_id
            ),
            None,
        )

        for i in range(start_index, end_index + 1):
            self.content[i][2] = (
                self.selected_category
                if self.content[i][2] == "transparent"
                else "transparent"
            )
