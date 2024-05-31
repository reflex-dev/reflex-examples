import reflex as rx
from typing import Literal, Union
from sqlmodel import select
from datetime import datetime, timedelta

LiteralStatus = Literal["Delivered", "Pending", "Cancelled"]


def _get_percentage_change(value: Union[int, float], prev_value: Union[int, float]) -> float:
    percentage_change = (
        round(((value - prev_value) / prev_value) * 100, 2)
        if prev_value != 0
        else 0
        if value == 0
        else
        float("inf")
    )
    return percentage_change

class Customer(rx.Model, table=True):
    """The customer model."""

    name: str
    email: str
    phone: str
    address: str
    date: str
    payments: float
    status: str


class MonthValues(rx.Base):
    """Values for a month."""

    num_customers: int = 0
    total_payments: float = 0.0
    num_delivers: int = 0



class State(rx.State):
    """The app state."""

    id: int
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    date: str = ""  # In 'YYYY-MM-DD HH:MM:SS' format
    payments: float = 0.0
    status: LiteralStatus = "Pending"
    users: list[Customer] = []
    sort_value: str = ""
    sort_reverse: bool = False
    # Values for current and previous month
    current_month_values: MonthValues = MonthValues()
    previous_month_values: MonthValues = MonthValues()

    def load_entries(self) -> list[Customer]:
        """Get all users from the database."""
        with rx.session() as session:
            self.users = session.exec(select(Customer)).all()
            if self.sort_value:
                if self.sort_value == "payments":
                    self.users = sorted(
                        self.users, key=lambda user: user.payments, reverse=self.sort_reverse
                    )
                else:
                    self.users = sorted(
                        self.users, key=lambda user: str(getattr(
                            user, self.sort_value)).lower(), reverse=self.sort_reverse
                    )
        self.get_current_month_values()
        self.get_previous_month_values()

    def get_current_month_values(self):
        """Calculate current month's values."""
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        current_month_users = [
            user for user in self.users if datetime.strptime(user.date, '%Y-%m-%d %H:%M:%S') >= start_of_month
        ]
        num_customers = len(current_month_users)
        total_payments = sum(user.payments for user in current_month_users)
        num_delivers = len([user for user in current_month_users if user.status == "Delivered"])
        self.current_month_values = MonthValues(num_customers=num_customers, total_payments=total_payments, num_delivers=num_delivers)

    def get_previous_month_values(self):
        """Calculate previous month's values."""
        now = datetime.now()
        first_day_of_current_month = datetime(now.year, now.month, 1)
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        start_of_last_month = datetime(last_day_of_last_month.year, last_day_of_last_month.month, 1)
        
        previous_month_users = [
            user for user in self.users
            if start_of_last_month <= datetime.strptime(user.date, '%Y-%m-%d %H:%M:%S') <= last_day_of_last_month
        ]
        # We add some dummy values to simulate growth/decline. Remove them in production.
        num_customers = len(previous_month_users) + 3
        total_payments = sum(user.payments for user in previous_month_users) + 240
        num_delivers = len([user for user in previous_month_users if user.status == "Delivered"]) + 5
        
        self.previous_month_values = MonthValues(num_customers=num_customers, total_payments=total_payments, num_delivers=num_delivers)

    def sort_values(self, sort_value: str):
        self.sort_value = sort_value
        self.load_entries()

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    def set_user_vars(self, user: Customer):
        self.id = user["id"]
        self.name = user["name"]
        self.email = user["email"]
        self.phone = user["phone"]
        self.address = user["address"]
        self.payments = user["payments"]
        self.status = user["status"]
        self.date = user["date"]

    def add_customer(self, form_data: dict):
        self.name = form_data.get("name")
        self.email = form_data.get("email")
        self.phone = form_data.get("phone")
        self.address = form_data.get("address")
        self.payments = form_data.get("payments")
        self.status = form_data.get("status", "Pending")
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        """Add a customer to the database."""
        with rx.session() as session:
            if session.exec(
                select(Customer).where(Customer.email == self.email)
            ).first():
                return rx._x.toast.info("User already exists", variant="outline", position="bottom-right")
            session.add(
                Customer(
                    name=self.name,
                    email=self.email,
                    phone=self.phone,
                    address=self.address,
                    payments=self.payments,
                    status=self.status,
                    date=self.date,
                )
            )
            session.commit()
        self.load_entries()
        return rx._x.toast.info(f"User {self.name} has been added.", variant="outline", position="bottom-right")

    def update_customer(self, form_data: dict):
        self.name = form_data.get("name")
        self.email = form_data.get("email")
        self.phone = form_data.get("phone")
        self.address = form_data.get("address")
        self.payments = form_data.get("payments")
        self.status = form_data.get("status", "Pending")

        """Update a customer in the database."""
        with rx.session() as session:
            customer = session.exec(
                select(Customer).where(Customer.id == self.id)
            ).first()
            customer.name = self.name
            customer.email = self.email
            customer.phone = self.phone
            customer.address = self.address
            customer.payments = self.payments
            customer.status = self.status
            session.add(customer)
            session.commit()
        self.load_entries()
        return rx._x.toast.info(f"User {self.name} has been modified.", variant="outline", position="bottom-right")

    def delete_customer(self, email: str):
        """Delete a customer from the database."""
        with rx.session() as session:
            customer = session.exec(
                select(Customer).where(Customer.email == email)
            ).first()
            session.delete(customer)
            session.commit()
        self.load_entries()
        return rx._x.toast.info(f"User {email} has been deleted.", variant="outline", position="bottom-right")

    def on_load(self):
        self.load_entries()
    
    @rx.var
    def payments_change(self) -> float:
        return _get_percentage_change(self.current_month_values.total_payments, self.previous_month_values.total_payments)

    @rx.var
    def customers_change(self) -> float:
        return _get_percentage_change(self.current_month_values.num_customers, self.previous_month_values.num_customers)

    @rx.var
    def delivers_change(self) -> float:
        return _get_percentage_change(self.current_month_values.num_delivers, self.previous_month_values.num_delivers)