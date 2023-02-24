"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
from .results import results

question_style = {
    "bg": "white",
    "padding": "2em",
    "border_radius": "25px",
    "w": "100%",
    "align_items": "left",
}


class State(pc.State):
    """The app state."""

    answers = ["False", "None", [False, False, False, False, False]]
    answer_key = ["False", "[10, 20, 30, 40]", [False, False, True, True, True]]
    score: int

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
            else:
                print(self.answers[i], self.answer_key[i])
            total += 1

        self.score = int(correct / total * 100)
        return pc.redirect("/result")


def header():
    return pc.vstack(
        pc.heading("Python Quiz"),
        pc.divider(),
        pc.text("Here is an example of a quiz made in Pynecone."),
        pc.text("Once submitted the results will be shown in the results page."),
        style=question_style,
    )


def question1():
    """The main view."""
    return pc.vstack(
        pc.heading("Question #1"),
        pc.text(
            "In Python 3, the maximum value for an integer is 26",
            pc.text("3", as_="sup"),
            " - 1",
        ),
        pc.divider(),
        pc.radio_group(
            ["True", "False"], on_change=lambda answer: State.set_answers(answer, 0)
        ),
        style=question_style,
    )


def question2():
    return pc.vstack(
        pc.heading("Question #2"),
        pc.text("What is the output of the following addition (+) operator?"),
        pc.code_block(
            """a = [10, 20]
b = a
b += [30, 40]
print(a)""",
            language="python",
        ),
        pc.radio_group(
            ["[10, 20, 30, 40]", "[10, 20]"],
            on_change=lambda answer: State.set_answers(answer, 1),
        ),
        style=question_style,
    )


def question3():
    return pc.vstack(
        pc.heading("Question #3"),
        pc.text(
            "Which of the following are valid ways to specify the string literal ",
            pc.code("foo'bar"),
            " in Python:",
        ),
        pc.vstack(
            pc.checkbox(
                pc.code("foo'bar"),
                on_change=lambda answer: State.set_answers(answer, 2, 0),
            ),
            pc.checkbox(
                pc.code("'foo''bar'"),
                on_change=lambda answer: State.set_answers(answer, 2, 1),
            ),
            pc.checkbox(
                pc.code("'foo\\\\'bar'"),
                on_change=lambda answer: State.set_answers(answer, 2, 2),
            ),
            pc.checkbox(
                pc.code('''"""foo'bar"""'''),
                on_change=lambda answer: State.set_answers(answer, 2, 3),
            ),
            pc.checkbox(
                pc.code('''"foo'bar"'''),
                on_change=lambda answer: State.set_answers(answer, 2, 4),
            ),
            align_items="left",
        ),
        style=question_style,
    )


def index():
    """The main view."""
    return pc.center(
        pc.vstack(
            header(),
            question1(),
            question2(),
            question3(),
            pc.button(
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


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Pynecone Quiz")
app.add_page(result, title="Quiz Results")
app.compile()
