import pynecone as pc

class CollaborativecounterConfig(pc.Config):
    pass

config = CollaborativecounterConfig(
    app_name="collaborative_counter",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)