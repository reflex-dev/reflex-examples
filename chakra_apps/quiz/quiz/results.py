import reflex as rx

answer_style = {
    "border_radius": "10px",
    "border": "1px solid #ededed",
    "padding": "0.5em",
    "align_items": "left",
    "shadow": "0px 0px 5px 0px #ededed",
}


def render_answer(State, index):
    return rx.chakra.tr(
        rx.chakra.td(index + 1),
        rx.chakra.td(
            rx.cond(
                State.answers[index].to_string() == State.answer_key[index].to_string(),
                rx.chakra.icon(tag="check", color="green"),
                rx.chakra.icon(tag="close", color="red"),
            )
        ),
        rx.chakra.td(State.answers[index].to_string()),
        rx.chakra.td(State.answer_key[index].to_string()),
    )


def results(State):
    """The results view."""
    return rx.chakra.center(
        rx.chakra.vstack(
            rx.chakra.heading("Results"),
            rx.chakra.text("Below are the results of the quiz."),
            rx.chakra.divider(),
            rx.chakra.center(
                rx.chakra.circular_progress(
                    rx.chakra.circular_progress_label(State.percent_score),
                    value=State.score,
                    size="3em",
                )
            ),
            rx.chakra.table(
                rx.chakra.thead(
                    rx.chakra.tr(
                        rx.chakra.th("#"),
                        rx.chakra.th("Result"),
                        rx.chakra.th("Your Answer"),
                        rx.chakra.th("Correct Answer"),
                    )
                ),
                rx.foreach(State.answers, lambda answer, i: render_answer(State, i)),
            ),
            rx.chakra.box(rx.chakra.link(rx.chakra.button("Take Quiz Again"), href="/")),
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
