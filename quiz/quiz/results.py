import reflex as rx
import reflex.components.radix.themes as rdxt

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
                rdxt.icon(tag="check", color="green"),
                rdxt.icon(tag="cross_1", color="red"),
            )
        ),
        rx.td(State.answers[index].to_string()),
        rx.td(State.answer_key[index].to_string()),
    )


def results(State):
    """The results view."""
    return rx.center(
        rx.vstack(
            rdxt.heading("Results", size="8"),
            rdxt.text("Below are the results of the quiz."),
            rdxt.separator(width="100%"),
            rx.center(
                rx.circular_progress(
                    rx.circular_progress_label(State.percent_score),
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
            rdxt.box(rdxt.link(rdxt.button("Take Quiz Again"), href="/")),
            background_color="white",
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
