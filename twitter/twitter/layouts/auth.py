import pynecone as pc


def auth_layout(*args):
    return pc.box(
        pc.vstack(
            pc.heading(
                pc.span("Welcome to PySocial!"),
                pc.span("Sign in or sign up to get started."),
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
            *args,
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
