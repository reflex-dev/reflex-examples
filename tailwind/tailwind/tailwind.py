"""Welcome to Pynecone! This file outlines the steps to create a basic app."""

import pynecone as pc
from pynecone import el


class State(pc.State):
    pass


def code_block(code: str, inline: bool = False):
    code_el = el.code(
        code,
        class_name=f"bg-gray-100 rounded text-sm font-mono {'p-1 mx-2 inline-block' if inline else 'block p-4'}",
    )
    if inline:
        return code_el
    return el.pre(
        code_el,
        class_name="block my-4",
    )


def toggle():
    return el.img(src="/tailwind.png", class_name="h-5")


PCCONFIG = """import pynecone as pc


class TailwindConfig(pc.Config):
    pass


config = TailwindConfig(
    app_name="tailwind",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
    tailwind={},
)
"""

EXAMPLE_TAILWIND_DICT = """{
        "theme": {
            "extend": {
                "colors": {
                    "primary": "#ff0000",
                    "secondary": "#00ff00",
                    "tertiary": "#0000ff"
                }
            }
        },
        "plugins": [
            "@tailwindcss/typography"
        ]
    }"""


def index() -> pc.Component:
    return el.div(
        toggle(),
        el.p(
            "This is a Pynecone app with Tailwind baked in.",
            class_name="text-gray-500 my-4",
        ),
        el.div(
            el.a(
                "Open Tailwind docs",
                href="https://tailwindcss.com/docs",
                target="_blank",
                class_name="font-semibold block border rounded-lg px-4 py-1 shadow-sm hover:bg-sky-500 hover:border-sky-500 hover:-translate-y-0.5 transition-all hover:shadow-lg hover:text-white",
            ),
            class_name="flex",
        ),
        el.hr(class_name="my-8"),
        el.p(
            "Just add a ",
            code_block("tailwind={}", True),
            "key to your config, and Pynecone takes care of the rest.",
        ),
        code_block(PCCONFIG),
        el.p(
            "You have access to the full Tailwind configuration API through the dictionary you pass in. Plugins will be automatically wrapped in",
            code_block("require()", True),
            ":",
        ),
        code_block(PCCONFIG.format(EXAMPLE_TAILWIND_DICT)),
        class_name="container mx-auto px-4 py-24 max-w-screen-md",
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.compile()
