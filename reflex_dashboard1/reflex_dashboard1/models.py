import reflex as rx


class User(rx.Model, table=True):
    first_name: str
    last_name: str


class Transactions(rx.Model, table=True):
    name: str
    category: str
    amount: str


class Cards(rx.Model, table=True):
    card_name: str
    card_number: str
    expiry: str
    current_balance: float

