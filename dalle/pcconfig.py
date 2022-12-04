import pynecone as pc


config = pc.Config(
    app_name="dalle",
    bun_path="$HOME/.bun/bin/bun",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
