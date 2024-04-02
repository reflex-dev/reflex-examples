import reflex as rx

answer_style = {
    "border_radius": "10px",
    "border": "1px solid #ededed",
    "padding": "0.5em",
    "align_items": "left",
    "shadow": "0px 0px 5px 0px #ededed",
}


def render_answer(State, index):
    return rx.table.row(
        rx.table.cell(index + 1),
        rx.table.cell(
            rx.cond(
                State.answers[index].to_string() == State.answer_key[index].to_string(),
                rx.icon(tag="check", color="green"),
                rx.icon(tag="x", color="red"),
            )
        ),
        rx.table.cell(State.answers[index].to_string()),
        rx.table.cell(State.answer_key[index].to_string()),
    )


def results(State):
    """The results view."""
    return rx.center(
        rx.vstack(
            rx.heading("Results"),
            rx.text("Below are the results of the quiz."),
            rx.divider(),
            rx.center(
                rx.chakra.circular_progress(
                    rx.chakra.circular_progress_label(State.percent_score),
                    value=State.score,
                    size="3em",
                )
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("#"),
                        rx.table.column_header_cell("Result"),
                        rx.table.column_header_cell("Your Answer"),
                        rx.table.column_header_cell("Correct Answer"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(State.answers, lambda answer, i: render_answer(State, i)),
                ),
            ),
            rx.box(rx.link(rx.button("Take Quiz Again"), href="/")),
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
