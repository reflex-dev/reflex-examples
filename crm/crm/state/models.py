import reflex as rx


class User(rx.Model, table=True):
    email: str
    password: str


class Contact(rx.Model, table=True):
    user_email: str
    contact_name: str
    email: str
    stage: str = "lead"
