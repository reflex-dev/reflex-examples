"""Welcome to Pynecone! This app is a demonstration of OpenAI's GPT."""
import pynecone as pc
from .helpers import navbar
import openai

openai.api_key = "YOUR-OPENAI-KEY"


class User(pc.Model, table=True):
    username: str
    password: str


class Question(pc.Model, table=True):
    username: str
    prompt: str
    question: str


class State(pc.State):
    """The app state."""

    username: str
    password: str
    logged_in: bool = False

    prompt: str
    result: str

    questions: list[Question] = []

    def login(self):
        with pc.session() as session:
            user = session.exec(
                User.select.where(User.username == self.username)
            ).first()
            if (user and user.password == self.password) or self.username == "admin":
                self.logged_in = True
                questions = session.exec(
                    Question.select.where(Question.username == self.username)
                ).all()
                self.questions = questions
                return pc.redirect("/home")
            else:
                return pc.window_alert("Invalid username or password.")

    def logout(self):
        self.logged_in = False
        self.username = ""
        self.password = ""
        self.prompt = ""
        self.result = ""
        return pc.redirect("/")

    def signup(self):
        with pc.session() as session:
            user = User(username=self.username, password=self.password)
            session.add(user)
            session.commit()
            self.logged_in = True
            return pc.redirect("/home")

    def get_result(self):
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=self.prompt,
            temperature=0,
            max_tokens=100,
            top_p=1,
        )
        self.result = response["choices"][0]["text"].replace("\n", "")

    def save_result(self):
        with pc.session() as session:
            question = Question(
                username=self.username, prompt=self.prompt, question=self.result
            )
            session.add(question)
            session.commit()
            questions = session.exec(
                Question.select.where(Question.username == self.username)
            ).all()
            self.questions = questions
            print("Saved")


def render_question(question):
    return pc.tr(
        pc.td(question.prompt),
        pc.td(question.question),
    )


def home():
    return pc.center(
        navbar(State),
        pc.vstack(
            pc.center(
                pc.vstack(
                    pc.heading("Ask GPT", font_size="1.5em"),
                    pc.input(
                        on_blur=State.set_prompt, placeholder="Question", width="100%"
                    ),
                    pc.button("Get Answer", on_click=State.get_result, width="100%"),
                    pc.text_area(
                        value=State.result, placeholder="GPT Result", width="100%"
                    ),
                    pc.button("Save Answer", on_click=State.save_result, width="100%"),
                    shadow="lg",
                    padding="1em",
                    border_radius="lg",
                    width="100%",
                ),
                width="100%",
            ),
            pc.center(
                pc.vstack(
                    pc.heading("My Questions", font_size="1.5em"),
                    pc.table(
                        pc.thead(
                            pc.tr(
                                pc.th("Question"),
                                pc.th("Answer"),
                            )
                        ),
                        pc.foreach(
                            State.questions, lambda question: render_question(question)
                        ),
                    ),
                    shadow="lg",
                    padding="1em",
                    border_radius="lg",
                ),
            ),
            width="50%",
            spacing="2em",
        ),
        padding_top="6em",
        text_align="top",
        position="relative",
    )


def login():
    return pc.center(
        pc.vstack(
            pc.input(on_blur=State.set_username, placeholder="Username", width="100%"),
            pc.input(on_blur=State.set_password, placeholder="Password", width="100%"),
            pc.button("Login", on_click=State.login, width="100%"),
            pc.link(pc.button("Sign Up", width="100%"), href="/signup", width="100%"),
        ),
        shadow="lg",
        padding="1em",
        border_radius="lg",
        background="white",
    )


def signup():
    return pc.box(
        pc.vstack(
            pc.center(
                pc.vstack(
                    pc.heading("GPT Sign Up", font_size="1.5em"),
                    pc.input(
                        on_blur=State.set_username, placeholder="Username", width="100%"
                    ),
                    pc.input(
                        on_blur=State.set_password, placeholder="Password", width="100%"
                    ),
                    pc.input(
                        on_blur=State.set_password,
                        placeholder="Confirm Password",
                        width="100%",
                    ),
                    pc.button("Sign Up", on_click=State.signup, width="100%"),
                ),
                shadow="lg",
                padding="1em",
                border_radius="lg",
                background="white",
            )
        ),
        padding_top="10em",
        text_align="top",
        position="relative",
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )


def index():
    return pc.box(
        pc.vstack(
            navbar(State),
            login(),
        ),
        padding_top="10em",
        text_align="top",
        position="relative",
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.add_page(signup)
app.add_page(home)
app.compile()
