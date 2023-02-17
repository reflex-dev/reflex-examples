import pynecone as pc

STAGES = ["Lead", "Opportunity", "Customer"]


class User(pc.Model, table=True):
    email: str
    password: str


class Contact(pc.Model, table=True):
    user_email: str
    contact_name: str
    email: str
    stage: str = STAGES[0]
