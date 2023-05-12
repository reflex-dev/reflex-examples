import pynecone as pc

class UploadConfig(pc.Config):
    pass

config = UploadConfig(
    app_name="upload",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
