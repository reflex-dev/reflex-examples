"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import reflex as rx
import copy
from .results import results
from typing import Any, List

question_style = {
    "bg": "white",
    "padding": "2em",
    "border_radius": "25px",
    "width": "100%",
    "align_items": "start",
}


class State(rx.State):
    """The app state."""

    default_answers = [None, None, [False, False, False, False, False]]
    answers: List[Any]
    answer_key = ["False", "[10, 20, 30, 40]", [False, False, True, True, True]]
    score: int

    def onload(self):
        self.answers = copy.deepcopy(self.default_answers)

    def set_answers(self, answer, index, sub_index=None):
        if sub_index is None:
            self.answers[index] = answer
        else:
            self.answers[index][sub_index] = answer

    def submit(self):
        total, correct = 0, 0
        for i in range(len(self.answers)):
            if self.answers[i] == self.answer_key[i]:
                correct += 1
            total += 1
        self.score = int(correct / total * 100)
        return rx.redirect("/result")

    @rx.var
    def percent_score(self):
        return f"{self.score}%"


def header():
    return rx.vstack(
        rx.heading("Python Quiz"),
        rx.divider(),
        rx.text("Here is an example of a quiz made in Reflex."),
        rx.text("Once submitted the results will be shown in the results page."),
        style=question_style,
    )


def question1():
    """The main view."""
    return rx.vstack(
        rx.heading("Question #1"),
        rx.text(
            "In Python 3, the maximum value for an integer is 26",
            rx.text("3", as_="sup"),
            " - 1",
        ),
        rx.divider(),
        rx.radio(
            items=["True", "False"],
            default_value=State.default_answers[0],
            default_checked=True,
            on_change=lambda answer: State.set_answers(answer, 0),
        ),
        style=question_style,
    )


def question2():
    return rx.vstack(
        rx.heading("Question #2"),
        rx.text("What is the output of the following addition (+) operator?"),
        rx.code_block(
            """a = [10, 20]
b = a
b += [30, 40]
print(a)""",
            language="python",
        ),
        rx.radio(
            items=["[10, 20, 30, 40]", "[10, 20]"],
            default_value=State.default_answers[1],
            default_check=True,
            on_change=lambda answer: State.set_answers(answer, 1),
        ),
        style=question_style,
    )


def question3():
    return rx.vstack(
        rx.heading("Question #3"),
        rx.text(
            "Which of the following are valid ways to specify the string literal ",
            rx.code("foo'bar"),
            " in Python:",
        ),
        rx.vstack(
            rx.checkbox(
                text=rx.code("foo'bar"),
                on_change=lambda answer: State.set_answers(answer, 2, 0),
            ),
            rx.checkbox(
                text=rx.code("'foo''bar'"),
                on_change=lambda answer: State.set_answers(answer, 2, 1),
            ),
            rx.checkbox(
                text=rx.code("'foo\\\\'bar'"),
                on_change=lambda answer: State.set_answers(answer, 2, 2),
            ),
            rx.checkbox(
                text=rx.code('''"""foo'bar"""'''),
                on_change=lambda answer: State.set_answers(answer, 2, 3),
            ),
            rx.checkbox(
                text=rx.code('''"foo'bar"'''),
                on_change=lambda answer: State.set_answers(answer, 2, 4),
            ),
            align_items="start",
        ),
        style=question_style,
    )


def index():
    """The main view."""
    return rx.center(
        rx.vstack(
            header(),
            question1(),
            question2(),
            question3(),
            rx.button(
                "Submit",
                bg="black",
                color="white",
                width="6em",
                padding="1em",
                on_click=State.submit,
            ),
            spacing="2",
        ),
        padding_y="2em",
        height="100vh",
        align_items="top",
        bg="#ededed",
        overflow="auto",
    )


def result():
    return results(State)


app = rx.App(
theme=rx.theme(
        has_background=True, radius="none", accent_color="orange", appearance="light",
    ),
)
app.add_page(index, title="Reflex Quiz", on_load=State.onload)
app.add_page(result, title="Quiz Results")
