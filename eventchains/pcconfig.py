import pynecone as pc


config = pc.Config(
    app_name="eventchains",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
