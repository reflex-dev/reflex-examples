"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from rxconfig import config

import reflex as rx
import reflex.components.radix.themes as rdxt
from sqlmodel import select

docs_url = "https://reflex.dev/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"



class Customer(rx.Model, table=True):
    """The customer model."""

    name: str
    email: str
    phone: str
    address: str




class State(rx.State):
    """The app state."""

    id: int
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    users: list[Customer] = []
    sort_value: str = ""
    num_customers: int


    def set_user_vars(self, user: Customer):
        print(user)
        self.id = user["id"]
        self.name = user["name"]
        self.email = user["email"]
        self.phone = user["phone"]
        self.address = user["address"]
         

    def add_customer(self):
        """Add a customer to the database"""

        with rx.session() as session:
            if session.exec(
                select(Customer).where(Customer.email == self.email)
            ).first():
                return rx.window_alert("User already exists")
            session.add(
                Customer(
                    name=self.name,
                    email=self.email,
                    phone=self.phone,
                    address=self.address,
                )
            )
            session.commit()
        return rx.window_alert(f"User {self.name} has been added.")


    def update_customer(self):
        """Update a customer in the database"""
        with rx.session() as session:
            customer = session.exec(
                select(Customer).where(Customer.id == self.id)
            ).first()
            customer.name = self.name
            customer.email = self.email
            customer.phone = self.phone
            customer.address = self.address
            print(customer)
            session.add(customer)
            session.commit()


    def delete_customer(self, email: str):
        """Delete a customer from the database."""
        with rx.session() as session:
            customer = session.exec(
                select(Customer).where(Customer.email == email)
            ).first()
            session.delete(customer)
            session.commit()



    @rx.var
    def get_users(self) -> list[Customer]:
        """Get all users from the database."""
        with rx.session() as session:
            self.users = session.exec(select(Customer)).all()
            self.num_customers = len(self.users)
            
            if self.sort_value:
                self.users = sorted(self.users, key=lambda user: getattr(user, self.sort_value).lower())
            return self.users


    


def show_customer(user: Customer):
    """Show a customer in a table row."""
    return rdxt.table_row(
                rdxt.table_cell(rdxt.avatar(fallback="DA")),
                rdxt.table_cell(user.name),
                rdxt.table_cell(user.email),
                rdxt.table_cell(user.phone),
                rdxt.table_cell(user.address),
                rdxt.table_cell(
                    update_customer(user),
                ),
                rdxt.table_cell(
                    rdxt.button(
                        "Delete",
                        on_click=lambda: State.delete_customer(user.email),
                        bg="red",
                        color="white",
                    ),
                ),
            )





def add_customer():
    return rdxt.dialog_root(
    rdxt.dialog_trigger(
        rdxt.button(rdxt.flex("Add New Customer", rdxt.icon(tag="plus", width=24, height=24), gap="3"), size="4", radius="full",),
    ),
    rdxt.dialog_content(
        rdxt.dialog_title("Customer Details", font_family="Inter",),
        rdxt.dialog_description(
            "Add your customer profile details.",
            size="2",
            mb="4",
        ),
        rdxt.flex(
            rdxt.text("Name", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder="Customer Name", on_blur=State.set_name),
            
            rdxt.text("Email", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder="Customer Email", on_blur=State.set_email),

            rdxt.text("Customer Phone", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder="Input Phone", on_blur=State.set_phone),

            rdxt.text("Customer Address", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder="Input Address", on_blur=State.set_address),
            direction="column",
            gap="3",
        ),
        rdxt.flex(
            rdxt.dialog_close(
                rdxt.button(
                    "Cancel",
                    variant="soft",
                    color_scheme="gray",
                ),
            ),
            rdxt.dialog_close(
                rdxt.button(
                    "Submit Customer", 
                    on_click=State.add_customer,
                    variant="solid",
                ),
            ),
            gap="3",
            mt="4",
            justify="end",
        ),
        style={"max_width": 450},
        box_shadow="lg",
        padding="1em",
        border="1px solid #ddd",
        border_radius="25px",
        font_family="Inter",
    ),

)


def update_customer(user):
    return rdxt.dialog_root(
    rdxt.dialog_trigger(
        rdxt.button(
            rdxt.icon(tag="pencil_2",width=24, height=24), 
            bg="red",
            color="white",
            on_click=lambda: State.set_user_vars(user)
        ),
    ),
    rdxt.dialog_content(
        rdxt.dialog_title("Customer Details"),
        rdxt.dialog_description(
            "Update your customer profile details.",
            size="2",
            mb="4",
        ),
        rdxt.flex(
            rdxt.text("Name", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder=user.name, default_value=user.name, on_blur=State.set_name),
            
            rdxt.text("Email", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder=user.email, default_value=user.email, on_blur=State.set_email),

            rdxt.text("Customer Phone", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder=user.phone, default_value=user.phone, on_blur=State.set_phone),

            rdxt.text("Customer Address", as_="div", size="2", mb="1", weight="bold",),
            rdxt.input(placeholder=user.address, default_value=user.address, on_blur=State.set_address),
            direction="column",
            gap="3",
        ),
        rdxt.flex(
            rdxt.dialog_close(
                rdxt.button(
                    "Cancel",
                    variant="soft",
                    color_scheme="gray",
                ),
            ),
            rdxt.dialog_close(
                rdxt.button(
                    "Submit Customer", 
                    on_click=State.update_customer,
                    variant="solid",
                ),
            ),
            gap="3",
            mt="4",
            justify="end",
        ),
        style={"max_width": 450},
        box_shadow="lg",
        padding="1em",
        border="1px solid #ddd",
        border_radius="25px",
    ),
)


def navbar():
    return rx.hstack(
        rdxt.heading("Customers", size="7", font_family="Inter"),
        rx.spacer(),
        add_customer(),
        rdxt.avatar(fallback="TG", size="4"),
        rx.color_mode_button(rx.color_mode_icon(), size="lg", float="right"),
        position="fixed",
        width="calc(100% - 250px)",
        top="0px",
        z_index="1000",
        padding_x="2em",
        padding_top="2em",
        padding_bottom="1em",
        backdrop_filter="blur(10px)",
    )


def content():
    return rx.fragment(
        rx.vstack(
            rdxt.separator(),
            rx.hstack(
                rdxt.heading(f"Total: {State.num_customers} Customers", size="5", font_family="Inter",),
                rx.spacer(),
                rdxt.select(["name", "email", "phone", "address"], placeholder="Sort By: Name", size="3", on_value_change=State.set_sort_value, font_family="Inter",),
                width="100%",
                padding_x="2em",
                padding_top="2em",
                padding_bottom="1em",
            ),
            rdxt.table_root(
                rdxt.table_header(
                    rdxt.table_row(
                        rdxt.table_column_header_cell("Icon"),
                        rdxt.table_column_header_cell("Name"),
                        rdxt.table_column_header_cell("Email"),
                        rdxt.table_column_header_cell("Phone"),
                        rdxt.table_column_header_cell("Address"),
                        rdxt.table_column_header_cell("Edit"),
                        rdxt.table_column_header_cell("Delete"),
                    ),
                ),
                rdxt.table_body(
                    rx.foreach(State.users, show_customer)
                ),
                #variant="surface",
                size="3",
                width="100%",
            ),
        ),
    )


def index() -> rx.Component:
    return rx.box(
            navbar(),
            rx.box(
                content(),
                margin_top="calc(50px + 2em)",
                padding="2em",
            ),
            padding_left="250px",
            font_family="Inter",
        )


# Create app instance and add index page.
app = rx.App(
    theme=rdxt.theme(
        appearance="light", has_background=True, radius="large", accent_color="grass"
    ),
    # stylesheets=[
    #     "https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap"
    # ],
    stylesheets=[
        "https://fonts.googleapis.com/css?family=Inter"
    ],
)
app.add_page(index)

