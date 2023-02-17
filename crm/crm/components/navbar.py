from crm.state import State, LoginState
import pynecone as pc


def navbar():
    return pc.box(
        pc.hstack(
            pc.link("Pyneknown", href="/", font_weight="medium"),
            pc.hstack(
                pc.cond(
                    State.user,
                    pc.hstack(
                        pc.link(
                            "Log out",
                            color="blue.300",
                            on_click=LoginState.log_out,
                        ),
                        pc.avatar(name=State.user.email, size="sm"),
                        spacing="1rem",
                    ),
                    pc.box(),
                )
            ),
            justify_content="space-between",
            max_width="960px",
            padding_x="0.5rem",
            padding_y="1rem",
            margin="0 auto"
        ),
        width="100%",
        margin_bottom="2rem",
        border_bottom="1px solid #eaeaef",
        background="#212121",
        color="#fff",
        box_shadow="0 5px 15px -5px #0003"
    )
