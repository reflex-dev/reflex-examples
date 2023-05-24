import pynecone as pc
from .base_state import State, User
from .components import navbar

styles = {
    "login_page": {
        "padding_top": "10em",
        "text_align": "top",
        "position": "relative",
        "background_image": "bg.svg",
        "background_size": "100% auto",
        "width": "100%",
        "height": "100vh",
    },
    "login_input": {
        "shadow": "lg",
        "padding": "1em",
        "border_radius": "lg",
        "background": "white",
    },
}


class AuthState(State):
    password: str
    confirm_password: str

    def signup(self):
        """Sign up a user."""
        with pc.session() as session:
            if self.password != self.confirm_password:
                return pc.window_alert("Passwords do not match.")
            if session.exec(User.select.where(User.username == self.username)).first():
                return pc.window_alert("Username already exists.")
            user = User(username=self.username, password=self.password)
            session.add(user)
            session.commit()
            self.logged_in = True
            return pc.redirect("/home")

    def login(self):
        """Log in a user."""
        with pc.session() as session:
            user = session.exec(
                User.select.where(User.username == self.username)
            ).first()
            if user and user.password == self.password:
                self.logged_in = True
                return pc.redirect("/home")
            else:
                return pc.window_alert("Invalid username or password.")


def signup():
    return pc.box(
        pc.vstack(
            navbar(State),
            pc.center(
                pc.vstack(
                    pc.heading("Sign Up", font_size="1.5em"),
                    pc.input(
                        on_blur=State.set_username, placeholder="Username", width="100%"
                    ),
                    pc.input(
                        on_blur=AuthState.set_password,
                        placeholder="Password",
                        width="100%",
                    ),
                    pc.input(
                        on_blur=AuthState.set_confirm_password,
                        placeholder="Confirm Password",
                        width="100%",
                    ),
                    pc.button("Sign Up", on_click=AuthState.signup, width="100%"),
                ),
                style=styles["login_input"],
            ),
        ),
        style=styles["login_page"],
    )


def login():
    return pc.box(
        pc.vstack(
            pc.heading(
                pc.span("Welcome to PyTwitter."),
                pc.span("Sign in to continue."),
                display="flex",
                flex_direction="column",
                align_items="center",
                text_align="center",
            ),
            pc.text(
                "See the source code for this demo app ",
                pc.link(
                    "here",
                    href="https://github.com/pynecone-io/pynecone-examples",
                    color="blue.500",
                ),
                ".",
                color="gray.500",
                font_weight="medium",
            ),
            pc.box(
                pc.input(placeholder="Username", on_blur=State.set_username, mb=4),
                pc.input(placeholder="Password", on_blur=AuthState.set_password, mb=4),
                pc.button(
                    "Log in",
                    on_click=AuthState.login,
                    bg="blue.500",
                    color="white",
                    _hover={"bg": "blue.600"},
                ),
                align_items="left",
                bg="white",
                border="1px solid #eaeaea",
                p=4,
                max_width="400px",
                border_radius="lg",
            ),
            pc.text(
                "Don't have an account yet? ",
                pc.link("Sign up here.", href="/signup", color="blue.500"),
                color="gray.600",
            ),
            template_columns="repeat(12, 1fr)",
            width="100%",
            max_width="960px",
            bg="white",
            h="100%",
            py=12,
            px=[4, 12],
            border_top_radius="lg",
            margin="0 auto",
            gap=4,
            box_shadow="0 4px 60px 0 rgba(0, 0, 0, 0.08), 0 4px 16px 0 rgba(0, 0, 0, 0.08)",
            position="relative",
        ),
        h="100vh",
        pt=16,
        background="url(bg.svg)",
        background_repeat="no-repeat",
        background_size="cover",
    )
