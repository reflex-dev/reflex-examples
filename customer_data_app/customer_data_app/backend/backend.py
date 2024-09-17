import reflex as rx
from typing import Literal, Union
from sqlmodel import select, asc, desc, or_, func, cast, String
from datetime import datetime, timedelta

#LiteralStatus = Literal["Delivered", "Pending", "Cancelled"]


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

    users: list[Customer] = []
    sort_value: str = ""
    sort_reverse: bool = False
    search_value: str = ""
    current_user: Customer = Customer()
    # Values for current and previous month
    current_month_values: MonthValues = MonthValues()
    previous_month_values: MonthValues = MonthValues()


    def load_entries(self) -> list[Customer]:
        """Get all users from the database."""
        with rx.session() as session:
            query = select(Customer)
            if self.search_value:
                search_value = f"%{str(self.search_value).lower()}%"
                query = query.where(
                    or_(
                        *[
                            getattr(Customer, field).ilike(search_value)
                            for field in Customer.get_fields()
                            if field not in ["id", "payments"]
                        ],
                        # ensures that payments is cast to a string before applying the ilike operator
                        cast(Customer.payments, String).ilike(search_value)
                    )
                )

            if self.sort_value:
                sort_column = getattr(Customer, self.sort_value)
                if self.sort_value == "payments":
                    order = desc(sort_column) if self.sort_reverse else asc(sort_column)
                else:
                    order = desc(func.lower(sort_column)) if self.sort_reverse else asc(func.lower(sort_column))
                query = query.order_by(order)
            
            self.users = session.exec(query).all()

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

    def filter_values(self, search_value):
        self.search_value = search_value
        self.load_entries()

    def get_user(self, user: Customer):
        self.current_user = user


    def add_customer_to_db(self, form_data: dict):
        self.current_user = form_data
        self.current_user["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with rx.session() as session:
            if session.exec(
                select(Customer).where(Customer.email == self.current_user["email"])
            ).first():
                return rx.window_alert("User with this email already exists")
            session.add(Customer(**self.current_user))
            session.commit()
        self.load_entries()
        return rx.toast.info(f"User {self.current_user['name']} has been added.", position="bottom-right")
    

    def update_customer_to_db(self, form_data: dict):
        self.current_user.update(form_data)
        with rx.session() as session:
            customer = session.exec(
                select(Customer).where(Customer.id == self.current_user["id"])
            ).first()
            for field in Customer.get_fields():
                if field != "id":
                    setattr(customer, field, self.current_user[field])
            session.add(customer)
            session.commit()
        self.load_entries()
        return rx.toast.info(f"User {self.current_user['name']} has been modified.", position="bottom-right")


    def delete_customer(self, id: int):
        """Delete a customer from the database."""
        with rx.session() as session:
            customer = session.exec(select(Customer).where(Customer.id == id)).first()
            session.delete(customer)
            session.commit()
        self.load_entries()
        return rx.toast.info(f"User {customer.name} has been deleted.", position="bottom-right")
    
    
    @rx.var
    def payments_change(self) -> float:
        return _get_percentage_change(self.current_month_values.total_payments, self.previous_month_values.total_payments)

    @rx.var
    def customers_change(self) -> float:
        return _get_percentage_change(self.current_month_values.num_customers, self.previous_month_values.num_customers)

    @rx.var
    def delivers_change(self) -> float:
        return _get_percentage_change(self.current_month_values.num_delivers, self.previous_month_values.num_delivers)