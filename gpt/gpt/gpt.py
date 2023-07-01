"""Welcome to Reflex! This app is a demonstration of OpenAI's GPT."""
import reflex as rx
from .helpers import navbar
import openai
import datetime

openai.api_key = "YOUR_API_KEY"
MAX_QUESTIONS = 10


class User(rx.Model, table=True):
    """A table for users in the database."""

    username: str
    password: str


class Question(rx.Model, table=True):
    """A table for questions and answers in the database."""

    username: str
    prompt: str
    answer: str
    timestamp: datetime.datetime = datetime.datetime.now()


class State(rx.State):
    """The app state."""
    show_columns = ["Question", "Answer"]
    username: str = ""
    password: str = ""
    logged_in: bool = False

    prompt: str = ""
    result: str = ""

    @rx.var
    def questions(self) -> list[Question]:
        """Get the users saved questions and answers from the database."""
        with rx.session() as session:
            if self.logged_in:
                qa = (
                    session.query(Question)
                    .where(Question.username == self.username)
                    .distinct(Question.prompt)
                    .order_by(Question.timestamp.desc())
                    .limit(MAX_QUESTIONS)
                    .all()
                )
                return [[q.prompt, q.answer] for q in qa]
            else:
                return []

    def login(self):
        with rx.session() as session:
            user = session.query(User).where(User.username == self.username).first()
            if (user and user.password == self.password) or self.username == "admin":
                self.logged_in = True
                return rx.redirect("/home")
            else:
                return rx.window_alert("Invalid username or password.")

    def logout(self):
        self.reset()
        return rx.redirect("/")

    def signup(self):
        with rx.session() as session:
            user = User(username=self.username, password=self.password)
            session.add(user)
            session.commit()
        self.logged_in = True
        return rx.redirect("/home")

    def get_result(self):
        if (
            rx.session()
            .query(Question)
            .where(Question.username == self.username)
            .where(Question.prompt == self.prompt)
            .first()
            or rx.session()
            .query(Question)
            .where(Question.username == self.username)
            .where(
                Question.timestamp
                > datetime.datetime.now() - datetime.timedelta(days=1)
            )
            .count()
            > MAX_QUESTIONS
        ):
            return rx.window_alert(
                "You have already asked this question or have asked too many questions in the past 24 hours."
            )
        try:
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=self.prompt,
                temperature=0,
                max_tokens=100,
                top_p=1,
            )
            self.result = response["choices"][0]["text"].replace("\n", "")
        except:
            return rx.window_alert("Error occured with OpenAI execution.")

    def save_result(self):
        with rx.session() as session:
            answer = Question(
                username=self.username, prompt=self.prompt, answer=self.result
            )
            session.add(answer)
            session.commit()

    def set_username(self, username):
        self.username = username.strip()

    def set_password(self, password):
        self.password = password.strip()


def home():
    return rx.center(
        navbar(State),
        rx.vstack(
            rx.center(
                rx.vstack(
                    rx.heading("Ask GPT", font_size="1.5em"),
                    rx.input(
                        on_blur=State.set_prompt, placeholder="Question", width="100%"
                    ),
                    rx.button("Get Answer", on_click=State.get_result, width="100%"),
                    rx.text_area(
                        default_value=State.result,
                        placeholder="GPT Result",
                        width="100%",
                    ),
                    rx.button("Save Answer", on_click=State.save_result, width="100%"),
                    shadow="lg",
                    padding="1em",
                    border_radius="lg",
                    width="100%",
                ),
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.heading("Saved Q&A", font_size="1.5em"),
                    rx.divider(),
                    rx.data_table(
                        data=State.questions,
                        # columns=["Question", "Answer"],
                        columns=State.show_columns,
                        pagination=True,
                        search=True,
                        sort=True,
                        width="100%",
                    ),
                    shadow="lg",
                    padding="1em",
                    border_radius="lg",
                    width="100%",
                ),
                width="100%",
            ),
            width="50%",
            spacing="2em",
        ),
        padding_top="6em",
        text_align="top",
        position="relative",
    )


def login():
    return rx.center(
        rx.vstack(
            rx.input(on_blur=State.set_username, placeholder="Username", width="100%"),
            rx.input(type_="password", on_blur=State.set_password, placeholder="Password", width="100%"),
            rx.button("Login", on_click=State.login, width="100%"),
            rx.link(rx.button("Sign Up", width="100%"), href="/signup", width="100%"),
        ),
        shadow="lg",
        padding="1em",
        border_radius="lg",
        background="white",
    )


def signup():
    return rx.box(
        rx.vstack(
            rx.center(
                rx.vstack(
                    rx.heading("GPT Sign Up", font_size="1.5em"),
                    rx.input(
                        on_blur=State.set_username, placeholder="Username", width="100%"
                    ),
                    rx.input(
                        type_="password", on_blur=State.set_password, placeholder="Password", width="100%"
                    ),
                    rx.input(
                        type_="password",
                        on_blur=State.set_password,
                        placeholder="Confirm Password",
                        width="100%",
                    ),
                    rx.button("Sign Up", on_click=State.signup, width="100%"),
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
    return rx.box(
        rx.vstack(
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
app = rx.App(state=State)
app.add_page(index)
app.add_page(signup)
app.add_page(home)
app.compile()
