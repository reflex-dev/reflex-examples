import pynecone as pc

class StablediffusionConfig(pc.Config):
    pass

config = StablediffusionConfig(
    app_name="stable_diffusion",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)