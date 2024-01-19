import reflex as rx
import reflex.components.radix.themes as rdxt

def navbar():
    return rdxt.box(
        rx.hstack(
            rx.hstack(
                rx.image(src="/nba.png", width="50px"),
                rdxt.heading("NBA Data", size="8"),
                rdxt.flex(
                    rdxt.badge("2015-2016 Season"),
                ),
            ),
            rdxt.dropdownmenu_root(
                rdxt.dropdownmenu_trigger(
                    rdxt.button("Menu", color="white", size="3", radius="medium", px=4, py=2),
                ),
                rdxt.dropdownmenu_content(
                    rdxt.link(rdxt.dropdownmenu_item("Graph"), href="/"),
                    rdxt.dropdownmenu_separator(),
                    rdxt.link(
                        rdxt.dropdownmenu_item(
                            rx.hstack(rdxt.text("20Dataset"), rdxt.icon(tag="download"))
                        ),
                        href="https://media.geeksforgeeks.org/wp-content/uploads/nba.csv",
                    ),
                ),
            ),
            justify="space-between",
            border_bottom="0.2em solid #F0F0F0",
            padding_x="2em",
            padding_y="1em",
            bg="rgba(255,255,255, 0.97)",
        ),
        position="fixed",
        width="100%",
        top="0px",
        z_index="500",
    )