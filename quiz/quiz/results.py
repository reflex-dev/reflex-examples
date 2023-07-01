import reflex as rx

answer_style = {
    "border_radius": "10px",
    "border": "1px solid #ededed",
    "padding": "0.5em",
    "align_items": "left",
    "shadow": "0px 0px 5px 0px #ededed",
}


def render_answer(State, index):
    return rx.tr(
        rx.td(index + 1),
        rx.td(
            rx.cond(
                State.answers[index].to_string() == State.answer_key[index].to_string(),
                rx.icon(tag="check", color="green"),
                rx.icon(tag="close", color="red"),
            )
        ),
        rx.td(State.answers[index].to_string()),
        rx.td(State.answer_key[index].to_string()),
    )


def results(State):
    """The results view."""
    return rx.center(
        rx.vstack(
            rx.heading("Results"),
            rx.text("Below are the results of the quiz."),
            rx.divider(),
            rx.center(
                rx.circular_progress(
                    rx.circular_progress_label(State.score + "%"),
                    value=State.score,
                    size="3em",
                )
            ),
            rx.table(
                rx.thead(
                    rx.tr(
                        rx.th("#"),
                        rx.th("Result"),
                        rx.th("Your Answer"),
                        rx.th("Correct Answer"),
                    )
                ),
                rx.foreach(State.answers, lambda answer, i: render_answer(State, i)),
            ),
            rx.link(rx.button("Take Quiz Again"), href="/"),
            bg="white",
            padding_x="5em",
            padding_y="2em",
            border_radius="25px",
            align_items="left",
            overflow="auto",
        ),
        padding="1em",
        height="100vh",
        align_items="top",
        bg="#ededed",
        overflow="auto",
    )
