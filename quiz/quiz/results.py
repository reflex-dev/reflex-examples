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
    return rdxt.table_row(
        rdxt.table_cell(index + 1),
        rdxt.table_cell(
            rx.cond(
                State.answers[index].to_string() == State.answer_key[index].to_string(),
                rdxt.icon(tag="check", color="green"),
                rdxt.icon(tag="cross_1", color="red"),
            )
        ),
        rdxt.table_cell(State.answers[index].to_string()),
        rdxt.table_cell(State.answer_key[index].to_string()),
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
            rdxt.table_root(
                rdxt.table_header(
                    rdxt.table_row(
                        rdxt.table_column_header_cell("#"),
                        rdxt.table_column_header_cell("Result"),
                        rdxt.table_column_header_cell("Your Answer"),
                        rdxt.table_column_header_cell("Correct Answer"),
                    ),
                ),
                rdxt.table_body(
                    rx.foreach(State.answers, lambda answer, i: render_answer(State, i)),
                ),
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
