import pynecone as pc

def navbar(State):
    return pc.box(
        pc.hstack(
            pc.link(pc.hstack(
                pc.image(src="favicon.ico"),
                pc.heading("Twitter Demo")
            ),
            href="/"),
            pc.menu(
                pc.menu_button(
                    pc.cond(
                        State.logged_in,
                        pc.avatar(name=State.username, size="md"),
                        pc.box()
                    )  
                ),
                pc.menu_list(
                    pc.center(
                        pc.vstack(
                        pc.avatar(name=State.username, size="md"),
                        pc.text(State.username)
                        )
                    ),
                    pc.menu_divider(),
                    pc.link(pc.menu_item("About GPT"), href="https://openai.com/api/"),
                    pc.link(pc.menu_item("Sign Out"), on_click=State.logout),
                ),
            ),
            justify="space-between",
            border_bottom="0.2em solid #F0F0F0",
            padding_x="2em",
            padding_y="1em",
            bg="rgba(255,255,255, 1)",
        ),
        position="fixed",
        width="100%",
        top="0px",
        z_index="500",
    )

def tweet(State):
    return pc.modal(
        pc.modal_overlay(
            pc.modal_content(
                pc.modal_header(
                    pc.hstack(
                        pc.icon(tag="CloseIcon", on_click=State.change, height=".8em", width=".8em"),
                        pc.spacer(),
                        pc.avatar(name=State.username, size="sm"),
                        width = "100%",
                    ),
                ),
                pc.modal_body(
                    pc.input(on_blur=State.set_tweet, placeholder="What's happening?", width="100%"),
                ),
                pc.modal_footer(
                    pc.button(
                        "Tweet", on_click=State.post_tweet,
                        bg="rgb(29 161 242)",
                        color="white",
                        border_radius="full",
                    )
                ),
            )
        ),
        is_open=State.show_tweet,
        border_radius="lg",
    )