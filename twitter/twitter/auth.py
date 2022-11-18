import pynecone as pc

def login(State):
    return pc.center(
        pc.vstack(
            pc.input(on_blur=State.set_username, placeholder="Username", width="100%"),
            pc.input(on_blur=State.set_password, placeholder="Password", type_="password", width="100%"),
            pc.button("Login", on_click=State.login, width="100%"),
            pc.link(pc.button("Sign Up", width="100%"), href="/signup", width="100%"),
        ),
        shadow = "lg",
        padding = "1em",
        border_radius = "lg",
        background = "white",
    )

def signup(State):
    return pc.box(
        pc.vstack(
            pc.center(
                pc.vstack(
                    pc.heading("Sign Up", font_size =  "1.5em"),
                    pc.input(on_blur=State.set_username, placeholder="Username", width="100%"),
                    pc.input(on_blur=State.set_password, placeholder="Password", width="100%"),
                    pc.input(on_blur=State.set_confirm_password, placeholder="Confirm Password", width="100%"),
                    pc.button("Sign Up", on_click= State.signup, width="100%"),
                ),
                shadow = "lg",
                padding = "1em",
                border_radius = "lg",
                background = "white",
            )
        ),
        padding_top = "10em",
        text_align="top",
        position = "relative",
        width = "100%",
        height = "100vh",
        background_image = "signup.svg",
        background_size =  "100% auto"
    )