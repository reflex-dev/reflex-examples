import pynecone as pc

class StablediffusionpyConfig(pc.Config):
    pass

config = StablediffusionpyConfig(
    app_name="stable_diffusion_py",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)