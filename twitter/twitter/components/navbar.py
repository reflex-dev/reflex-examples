"""The navbar component."""
import pynecone as pc


def navbar(State):
    """The navbar."""
    return pc.box(
        pc.hstack(
            pc.link(
                "Twitter Demo",
                font_weight="bold",
                href="/",
            ),
            pc.menu(
                pc.menu_button(
                    pc.cond(
                        State.logged_in,
                        pc.avatar(name=State.username, size="md"),
                        pc.box(),
                    )
                ),
                pc.menu_list(
                    pc.center(
                        pc.vstack(
                            pc.avatar(name=State.username, size="md"),
                            pc.text(State.username),
                        )
                    ),
                    pc.menu_divider(),
                    pc.link(pc.menu_item("Sign Out"), on_click=State.logout),
                ),
            ),
            justify="space-between",
            bg="white",
            max_width="960px",
            margin="0 auto",
            px=8,
            py=4,
        ),
        position="sticky",
        border_bottom="1px solid #eaeaef",
        width="100%",
        top=0,
        z_index="500",
    )
