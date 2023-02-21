import pynecone as pc

answer_style = {
    "border_radius": "10px",
    "border": "1px solid #ededed",
    "padding": "0.5em",
    "align_items": "left",
    "shadow": "0px 0px 5px 0px #ededed",
}


def render_answer(State, index):
    return pc.tr(
        pc.td(index + 1),
        pc.td(
            pc.cond(
                State.answers[index].to_string() == State.answer_key[index].to_string(),
                pc.icon(tag="check", color="green"),
                pc.icon(tag="close", color="red"),
            )
        ),
        pc.td(State.answers[index].to_string()),
        pc.td(State.answer_key[index].to_string()),
    )


def results(State):
    """The results view."""
    return pc.center(
        pc.vstack(
            pc.heading("Results"),
            pc.text("Below are the results of the quiz."),
            pc.divider(),
            pc.center(
                pc.circular_progress(
                    pc.circular_progress_label(State.score + "%"),
                    value=State.score,
                    size="3em",
                )
            ),
            pc.table(
                pc.thead(
                    pc.tr(
                        pc.th("#"),
                        pc.th("Result"),
                        pc.th("Your Answer"),
                        pc.th("Correct Answer"),
                    )
                ),
                pc.foreach(State.answers, lambda answer, i: render_answer(State, i)),
            ),
            pc.link(pc.button("Take Quiz Again"), href="/"),
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
