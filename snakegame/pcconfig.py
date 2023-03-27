import pynecone as pc

config = pc.Config(
    app_name="snakegame",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
