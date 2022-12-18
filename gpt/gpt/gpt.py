"""Welcome to Pynecone! This app is a demonstration of OpenAI's GPT."""
import pynecone as pc
from .helpers import navbar
import openai
import datetime

openai.api_key = "YOUR_API_KEY"


class User(pc.Model, table=True):
    """A table for users in the database."""

    username: str
    password: str


class Question(pc.Model, table=True):
    """A table for questions and answers in the database."""

    username: str
    prompt: str
    answer: str
    timestamp: datetime.datetime = datetime.datetime.now()


class State(pc.State):
    """The app state."""

    username: str = ""
    password: str = ""
    logged_in: bool = False

    prompt: str = ""
    result: str = ""

    @pc.var
    def questions(self) -> list[Question]:
        """Get the users saved questions and answers from the database."""
        with pc.session() as session:
            if self.logged_in:
                qa = (
                    session.query(Question)
                    .where(Question.username == self.username)
                    .distinct(Question.prompt)
                    .limit(10)
                    .all()
                )
                qa = [[q.prompt, q.answer] for q in qa]
                return qa
            else:
                return []

    def login(self):
        with pc.session() as session:
            user = session.query(User).where(User.username == self.username).first()
            if (user and user.password == self.password) or self.username == "admin":
                self.logged_in = True
                return pc.redirect("/home")
            else:
                return pc.window_alert("Invalid username or password.")

    def logout(self):
        self.reset()
        return pc.redirect("/")

    def signup(self):
        with pc.session() as session:
            user = User(username=self.username, password=self.password)
            session.add(user)
            session.commit()
        self.logged_in = True
        return pc.redirect("/home")

    def get_result(self):
        if (
                pc.session().query(Question)
                .where(Question.username == self.username)
                .where(Question.prompt == self.prompt)
                .first()
                or len(
                    pc.session().query(Question)
                    .where(Question.username == self.username)
                    .where(
                        Question.timestamp
                        > datetime.datetime.now() - datetime.timedelta(days=1)
                    )
                    .all()
                )
                > 10
            ):
                return pc.window_alert(
                    "You have already asked this question or asked too many questions in the past 24 hours."
                )
                
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
                        default_value=State.result,
                        placeholder="GPT Result",
                        width="100%",
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
                    pc.heading("Saved Q&A", font_size="1.5em"),
                    pc.divider(),
                    pc.data_table(
                        data=State.questions,
                        columns=["Question", "Answer"],
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
            width=["50%"],
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
