import pynecone as pc


class TailwindConfig(pc.Config):
    pass


config = TailwindConfig(
    app_name="tailwind",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
    tailwind={},
)
