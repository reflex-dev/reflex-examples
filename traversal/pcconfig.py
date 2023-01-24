import pynecone as pc


config = pc.Config(
    app_name="traversal",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
