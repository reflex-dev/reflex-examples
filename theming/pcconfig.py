import pynecone as pc


class ThemingConfig(pc.Config):
    pass


config = ThemingConfig(
    app_name="theming",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
