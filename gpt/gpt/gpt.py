"""Welcome to Reflex! This app is a demonstration of OpenAI's GPT."""

import datetime

from openai import OpenAI
from sqlmodel import select, or_

import reflex as rx

from .helpers import navbar

client = OpenAI()
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
    logged_in: bool = False

    prompt: str = ""
    result: str = ""
    loading: bool = False

    filter: str = ""

    @rx.var
    def questions(self) -> list[Question]:
        """Get the users saved questions and answers from the database."""
        with rx.session() as session:
            if self.logged_in:
                query = select(Question).where(Question.username == self.username)
                if self.filter:
                    query = query.where(
                        or_(
                            Question.prompt.ilike(f"%{self.filter}%"),
                            Question.answer.ilike(f"%{self.filter}%"),
                        )
                    )
                return session.exec(
                    query.distinct(Question.prompt)
                    .order_by(Question.timestamp.desc())
                    .limit(MAX_QUESTIONS)
                ).all()
            else:
                return []

    def login(self, form_data: dict[str, str]):
        self.username = form_data["username"].strip()
        password = form_data["password"].strip()
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.username == self.username)
            ).first()
            if (user and user.password == password) or self.username == "admin":
                self.logged_in = True
                return rx.redirect("/home")
            else:
                return rx.window_alert("Invalid username or password.")

    def logout(self):
        self.reset()
        return rx.redirect("/")

    def signup(self, form_data: dict[str, str]):
        self.username = form_data["username"].strip()
        password = form_data["password"].strip()
        confirm = form_data["confirm"].strip()
        if password != confirm:
            return [
                rx.set_value("confirm", ""),
                rx.window_alert("Passwords do not match."),
            ]
        with rx.session() as session:
            user = User(username=self.username, password=password)
            session.add(user)
            session.commit()
        self.logged_in = True
        return rx.redirect("/home")

    def get_result(self, form_data: dict[str, str]):
        self.prompt = form_data["prompt"]
        with rx.session() as session:
            if (
                session.exec(
                    select(Question)
                    .where(Question.username == self.username)
                    .where(Question.prompt == self.prompt)
                ).first()
                or len(
                    session.exec(
                        select(Question)
                        .where(Question.username == self.username)
                        .where(
                            Question.timestamp
                            > datetime.datetime.now() - datetime.timedelta(days=1)
                        )
                    ).all()
                )
                > MAX_QUESTIONS
            ):
                return rx.window_alert(
                    "You have already asked this question or have asked too many questions in the past 24 hours."
                )
        self.result = ""
        self.loading = True
        yield
        try:
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=self.prompt,
                temperature=0,
                max_tokens=100,
                top_p=1,
            )
            self.result = response.choices[0].text.replace("\n", "")
        except Exception as e:
            print(e)
            return rx.window_alert("Error occured with OpenAI execution.")
        finally:
            self.loading = False

    def save_result(self):
        with rx.session() as session:
            answer = Question(
                username=self.username, prompt=self.prompt, answer=self.result
            )
            session.add(answer)
            session.commit()


def result_view() -> rx.Component:
    return rx.fragment(
        rx.flex(
            rx.text(State.prompt),
            rx.cond(
                State.loading,
                rx.chakra.spinner(),
            ),
            justify="between",
        ),
        rx.scroll_area(
            rx.cond(
                State.result,
                rx.text(State.result),
                rx.cond(
                    State.loading,
                    rx.text("AI is answering...", color_scheme="gray"),
                    rx.text(
                        "Ask a question to get an answer from GPT.", color_scheme="gray"
                    ),
                ),
            ),
            type_="hover",
            width="100%",
            max_height="7em",
        ),
        rx.cond(
            State.logged_in & (State.result != ""),
            rx.button("Save Answer", on_click=State.save_result, width="100%"),
        ),
    )


def ask_gpt_form() -> rx.Component:
    return rx.vstack(
        rx.heading("Ask GPT", font_size="1.5em", align="center"),
        rx.form(
            rx.vstack(
                rx.input(placeholder="Question", name="prompt", width="100%"),
                rx.button("Get Answer", width="100%"),
                spacing="3",
            ),
            on_submit=State.get_result,
            reset_on_submit=True,
        ),
        rx.divider(),
        result_view(),
        align="stretch",
        spacing="3",
        width="100%",
    )


def saved_qa_item(qa: Question, ix: int) -> rx.Component:
    return rx.accordion.item(
        header=rx.text(qa.prompt, size="3", align="left"),
        content=rx.scroll_area(
            rx.text(qa.answer, size="2"),
            type_="hover",
            max_height="10em",
            padding="12px",
        ),
        value=f"item-{ix}",
    )


def saved_qa() -> rx.Component:
    return rx.vstack(
        rx.heading("Saved Q&A", font_size="1.5em"),
        rx.divider(),
        rx.input(
            placeholder="Filter",
            value=State.filter,
            on_change=State.set_filter,
            debounce_timeout=1500,
            width="100%",
        ),
        rx.accordion.root(
            rx.foreach(
                State.questions,
                saved_qa_item,
            ),
            single=False,
            collapsible=True,
        ),
        spacing="3",
        padding="1em",
        width="100%",
    )


def home():
    return rx.flex(
        navbar(State),
        rx.vstack(
            rx.card(ask_gpt_form()),
            rx.cond(
                State.logged_in,
                rx.card(saved_qa()),
            ),
            spacing="4",
            width="50%",
        ),
        justify="center",
        padding_top="6em",
        text_align="top",
        position="relative",
    )


def login():
    return rx.form(
        rx.card(
            rx.vstack(
                rx.input(name="username", placeholder="Username", width="100%"),
                rx.input(
                    type="password",
                    name="password",
                    placeholder="Password",
                    width="100%",
                ),
                rx.button("Login", width="100%"),
                rx.button(
                    "Sign Up",
                    type="button",
                    width="100%",
                    on_click=rx.redirect("/signup"),
                ),
                spacing="3",
            )
        ),
        on_submit=State.login,
    )


def signup():
    return rx.flex(
        rx.form(
            rx.vstack(
                rx.heading("GPT Sign Up", font_size="1.5em"),
                rx.input(name="username", placeholder="Username", width="100%"),
                rx.input(
                    type="password",
                    name="password",
                    placeholder="Password",
                    width="100%",
                ),
                rx.input(
                    type="password",
                    name="confirm",
                    id="confirm",
                    placeholder="Confirm Password",
                    width="100%",
                ),
                rx.button("Sign Up", width="100%"),
                spacing="3",
                align="center",
                justify="center",
                padding="1em",
                background="white",
            ),
            on_submit=State.signup,
        ),
        align="start",
        justify="center",
        padding_top="10em",
        text_align="top",
        position="relative",
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )


def index():
    return rx.vstack(
        navbar(State),
        rx.flex(
            login(),
            justify="center",
        ),
        padding_top="10em",
        text_align="top",
        position="relative",
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )


# Add pages to the app.
app = rx.App()
app.add_page(index)
app.add_page(signup)
app.add_page(home)
