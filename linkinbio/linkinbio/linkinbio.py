import reflex as rx
from linkinbio.style import *

# add launchdarkly imports
import ldclient
from ldclient.config import Config
from ldclient import Context
import os

# Initialize LD client (this should be done once, typically at app startup)
SDK_KEY = os.getenv("LD_SDK_KEY")
print(SDK_KEY)
ldclient.set_config(Config("sdk-bfe7db54-0861-4928-8c35-3bc8daf8e0a6"))
LD_CLIENT = ldclient.get()
LD_CONTEXT: Context | None = None


class State(rx.State):

    # Create a LaunchDarkly context (formerly known as "user")
    ld_context_set: bool = False

    def build_ld_context(
        self,
        feature_flag_key: str = "toggle-bio",
    ) -> None:
        global LD_CONTEXT
        LD_CONTEXT = (
            Context.builder(
                "context-key-123abc",
            )
            .name(
                "Sandy",
            )
            .build()
        )
        self.ld_context_set = True

    @rx.var
    def get_feature_flag_bool(
        self,
        feature_flag_key: str = "toggle-bio",
    ) -> bool:
        if not self.ld_context_set:
            return False

        print("LD_CONTEXT", LD_CONTEXT)
        flag_value: bool = LD_CLIENT.variation(
            key=feature_flag_key,
            context=LD_CONTEXT,
            default=False,
        )
        print(f"Flag value: {flag_value}")
        return flag_value

def link_button(
    name: str,
    url: str,
    icon: str,
) -> rx.Component:
    icon_map = {
        "globe": "globe",
        "twitter": "twitter",
        "github": "github",
        "linkedin": "linkedin",
    }
    icon_tag = icon_map.get(
        icon.lower(),
        "link",
    )
    return rx.link(
        rx.button(
            rx.icon(
                tag=icon_tag,
            ),
            name,
            width="100%",
        ),
        href=url,
        is_external=True,
    )


def index_content(
    name: str,
    pronouns: str,
    bio: str,
    avatar_url: str,
    links: list[dict[str, str]],
    background: str,
):
    return rx.center(
        rx.vstack(
            rx.avatar(
                src=avatar_url,
                size="2xl",
            ),
            rx.heading(
                name,
                size="lg",
            ),
            rx.text(
                pronouns,
                font_size="sm",
            ),
            rx.text(bio),
            rx.vstack(
                rx.foreach(
                    links,
                    lambda link: link_button(link["name"], link["url"], link["icon"]),
                ),
                width="100%",
                spacing="2",
            ),
            padding="4",
            max_width="400px",
            width="100%",
            spacing="3",
        ),
        width="100%",
        height="100vh",
        background=background,
    )


def index() -> rx.Component:
    # Define the component and background based on the feature flag
    # if State.get_feature_flag_bool:
    # name = "Erin Mikail Staples"
    # background = "linear-gradient(45deg, #FFD700, #FF8C00, #FF4500)"
    # pronouns = "she/her/hers"
    # bio = "Stand up comedian + co-producer of the Inside Jokes show at Grisly Pear Comedy Club"
    # avatar_url = "https://avatars.githubusercontent.com/erinmikailstaples"
    # links = [
    #     {"name": "Website", "url": "https://www.insidejokes.nyc/"},
    #     {"name": "Upcoming Events", "url": "lu.ma/erinmikail"},
    #     {"name": "Instagram", "url": "https://instagram.com/erinmikail"},
    #     {"name": "Inside Jokes NYC", "url": "https://instagram.com/insidejokesnyc"},
    # ]

    # else:
    #     name = "Erin Mikail Staples"
    #     background = "radial-gradient(circle, var(--chakra-colors-purple-100), var(--chakra-colors-blue-100))"
    #     pronouns = "she/her/hers"
    #     bio = "Developer Experience Engineer @ LaunchDarkly"
    #     avatar_url = "https://avatars.githubusercontent.com/erinmikailstaples"
    #     links = [
    #         {
    #             "name": "Website",
    #             "url": "https://erinmikailstaples.com",
    #             "icon": "globe",
    #         },
    #         {
    #             "name": "Twitter",
    #             "url": "https://twitter.com/erinmikail",
    #             "icon": "twitter",
    #         },
    #         {
    #             "name": "GitHub",
    #             "url": "https://github.com/erinmikailstaples",
    #             "icon": "github",
    #         },
    #         {
    #             "name": "LinkedIn",
    #             "url": "https://linkedin.com/in/erinmikail",
    #             "icon": "linkedin",
    #         },
    #     ]
    return rx.cond(
        State.get_feature_flag_bool,
        index_content(
            name="Toggle-bio True",
            pronouns="she/her/hers",
            bio="Stand up comedian + co-producer of the Inside Jokes show at Grisly Pear Comedy Club",
            avatar_url="https://avatars.githubusercontent.com/erinmikailstaples",
            links=[
                {"name": "Website", "url": "https://www.insidejokes.nyc/"},
                {"name": "Upcoming Events", "url": "lu.ma/erinmikail"},
                {"name": "Instagram", "url": "https://instagram.com/erinmikail"},
                {
                    "name": "Inside Jokes NYC",
                    "url": "https://instagram.com/insidejokesnyc",
                },
            ],
            background="linear-gradient(45deg, #FFD700, #FF8C00, #FF4500)",
        ),
        index_content(
            name="Toggle-bio False",
            pronouns="she/her/hers",
            bio="Developer Experience Engineer @ LaunchDarkly",
            avatar_url="https://avatars.githubusercontent.com/erinmikailstaples",
            links=[
                {
                    "name": "Website",
                    "url": "https://erinmikailstaples.com",
                    "icon": "globe",
                },
                {
                    "name": "Twitter",
                    "url": "https://twitter.com/erinmikail",
                    "icon": "twitter",
                },
                {
                    "name": "GitHub",
                    "url": "https://github.com/erinmikailstaples",
                    "icon": "github",
                },
                {
                    "name": "LinkedIn",
                    "url": "https://linkedin.com/in/erinmikail",
                    "icon": "linkedin",
                },
            ],
            background="radial-gradient(circle, var(--chakra-colors-purple-100), var(--chakra-colors-blue-100))",
        ),
    )


app = rx.App(
    style=style,
)
app.add_page(
    index,
    on_load=State.build_ld_context,
)
