"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import reflex as rx
import reflex.components.radix.themes as rdxt
import copy
from .results import results
from typing import Any
from typing import List

question_style = {
    "bg": "white",
    "padding": "2em",
    "border_radius": "25px",
    "w": "100%",
    "align_items": "left",
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
        rdxt.heading("Python Quiz", size="9"),
        rdxt.separator(width="100%"),
        rdxt.text("Here is an example of a quiz made in Reflex."),
        rdxt.text("Once submitted the results will be shown in the results page."),
        style=question_style,
    )


def question1():
    """The main view."""
    return rx.vstack(
        rdxt.heading("Question #1", size="8"),
        rdxt.text(
            "In Python 3, the maximum value for an integer is 26",
            rdxt.text("3", as_="sup"),
            " - 1",
        ),
        rdxt.separator(width="100%"),
        rdxt.radio_group(
            items=["True", "False"],
            on_value_change=lambda answer: State.set_answers(answer, 0),
            direction="row",
            default_value=True,
        ),
        style=question_style,
    )


def question2():
    return rx.vstack(
        rdxt.heading("Question #2", size="8"),
        rdxt.text("What is the output of the following addition (+) operator?"),
        rx.code_block(
            """a = [10, 20]
b = a
b += [30, 40]
print(a)""",
            language="python",
        ),
        rdxt.radio_group(
            items= ["[10, 20, 30, 40]", "[10, 20]"],
            on_value_change=lambda answer: State.set_answers(answer, 1),
            direction="row",
            default_value=State.default_answers[1],
        ),
        style=question_style,
    )


def question3():
    return rx.vstack(
        rdxt.heading("Question #3", size="8"),
        rdxt.text(
            "Which of the following are valid ways to specify the string literal ",
            rx.code("foo'bar"),
            " in Python:",
        ),
        rx.vstack(
            rdxt.checkbox_hl(
                text=rx.code("foo'bar"),
                on_checked_change=lambda answer: State.set_answers(answer, 2, 0),
            ),
            rdxt.checkbox_hl(
                text=rx.code("'foo''bar'"),
                on_checked_change=lambda answer: State.set_answers(answer, 2, 1),
            ),
            rdxt.checkbox_hl(
                text=rx.code("'foo\\\\'bar'"),
                on_checked_change=lambda answer: State.set_answers(answer, 2, 2),
            ),rdxt.checkbox_hl(
                text=rx.code('''"""foo'bar"""'''),
                on_checked_change=lambda answer: State.set_answers(answer, 2, 3),
            ),
            rdxt.checkbox_hl(
                text=rx.code('''"foo'bar"'''),
                on_checked_change=lambda answer: State.set_answers(answer, 2, 4),
            ),
            align_items="left",
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
            spacing="1em",
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
    theme=rdxt.theme(
            has_background=True, radius="none", accent_color="grass", appearance="light",
        ),
)
app.add_page(index, title="Reflex Quiz", on_load=State.onload)
app.add_page(result, title="Quiz Results")
