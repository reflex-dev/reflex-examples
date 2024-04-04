"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from sqlmodel import select

import reflex as rx


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

    def load_entries(self) -> list[Customer]:
        """Get all users from the database."""
        with rx.session() as session:
            self.users = session.exec(select(Customer)).all()
            self.num_customers = len(self.users)

            if self.sort_value:
                self.users = sorted(
                    self.users, key=lambda user: getattr(user, self.sort_value).lower()
                )

    def sort_values(self, sort_value: str):
        self.sort_value = sort_value
        self.load_entries()

    def set_user_vars(self, user: Customer):
        print(user)
        self.id = user["id"]
        self.name = user["name"]
        self.email = user["email"]
        self.phone = user["phone"]
        self.address = user["address"]

    def add_customer(self):
        """Add a customer to the database."""
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
        self.load_entries()
        return rx.window_alert(f"User {self.name} has been added.")

    def update_customer(self):
        """Update a customer in the database."""
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
        self.load_entries()

    def delete_customer(self, email: str):
        """Delete a customer from the database."""
        with rx.session() as session:
            customer = session.exec(
                select(Customer).where(Customer.email == email)
            ).first()
            session.delete(customer)
            session.commit()
        self.load_entries()

    def on_load(self):
        self.load_entries()


def show_customer(user: Customer):
    """Show a customer in a table row."""
    return rx.table.row(
        rx.table.cell(rx.avatar(fallback="DA")),
        rx.table.cell(user.name),
        rx.table.cell(user.email),
        rx.table.cell(user.phone),
        rx.table.cell(user.address),
        rx.table.cell(
            update_customer(user),
        ),
        rx.table.cell(
            rx.button(
                "Delete",
                on_click=lambda: State.delete_customer(user.email),
                color_scheme="red",
                color="white",
            ),
        ),
    )


def add_customer():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.flex(
                    "Add New Customer",
                    rx.icon(tag="plus", width=24, height=24),
                    spacing="3",
                ),
                size="4",
                radius="full",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Customer Details",
                font_family="Inter",
            ),
            rx.dialog.description(
                "Add your customer profile details.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rx.text(
                    "Name",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(placeholder="Customer Name", on_blur=State.set_name),
                rx.text(
                    "Email",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(placeholder="Customer Email", on_blur=State.set_email),
                rx.text(
                    "Customer Phone",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(placeholder="Input Phone", on_blur=State.set_phone),
                rx.text(
                    "Customer Address",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(placeholder="Input Address", on_blur=State.set_address),
                direction="column",
                spacing="3",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Submit Customer",
                        on_click=State.add_customer,
                        variant="solid",
                    ),
                ),
                padding_top="1em",
                spacing="3",
                mt="4",
                justify="end",
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="1em",
            border_radius="25px",
            font_family="Inter",
        ),
    )


def update_customer(user):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("square_pen", width=24, height=24),
                color_scheme="red",
                color="white",
                on_click=lambda: State.set_user_vars(user),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Customer Details"),
            rx.dialog.description(
                "Update your customer profile details.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rx.text(
                    "Name",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder=user.name,
                    default_value=user.name,
                    on_blur=State.set_name,
                ),
                rx.text(
                    "Email",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder=user.email,
                    default_value=user.email,
                    on_blur=State.set_email,
                ),
                rx.text(
                    "Customer Phone",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder=user.phone,
                    default_value=user.phone,
                    on_blur=State.set_phone,
                ),
                rx.text(
                    "Customer Address",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder=user.address,
                    default_value=user.address,
                    on_blur=State.set_address,
                ),
                direction="column",
                spacing="3",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Submit Customer",
                        on_click=State.update_customer,
                        variant="solid",
                    ),
                ),
                padding_top="1em",
                spacing="3",
                mt="4",
                justify="end",
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="1em",
            border_radius="25px",
        ),
    )


def navbar():
    return rx.hstack(
        rx.vstack(
            rx.heading("Customer Data App", size="7", font_family="Inter"),
        ),
        rx.spacer(),
        add_customer(),
        rx.avatar(fallback="TG", size="4"),
        rx.color_mode.button(rx.color_mode.icon(), size="3", float="right"),
        position="fixed",
        width="100%",
        top="0px",
        z_index="1000",
        padding_x="4em",
        padding_top="2em",
        padding_bottom="1em",
        backdrop_filter="blur(10px)",
    )


def content():
    return rx.fragment(
        rx.vstack(
            rx.divider(),
            rx.hstack(
                rx.heading(
                    f"Total: {State.num_customers} Customers",
                    size="5",
                    font_family="Inter",
                ),
                rx.spacer(),
                rx.select(
                    ["name", "email", "phone", "address"],
                    placeholder="Sort By: Name",
                    size="3",
                    on_change=lambda sort_value: State.sort_values(sort_value),
                    font_family="Inter",
                ),
                width="100%",
                padding_x="2em",
                padding_top="2em",
                padding_bottom="1em",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Icon"),
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Email"),
                        rx.table.column_header_cell("Phone"),
                        rx.table.column_header_cell("Address"),
                        rx.table.column_header_cell("Edit"),
                        rx.table.column_header_cell("Delete"),
                    ),
                ),
                rx.table.body(rx.foreach(State.users, show_customer)),
                # variant="surface",
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
            padding="4em",
        ),
        font_family="Inter",
    )


# Create app instance and add index page.
app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="grass"
    ),
    stylesheets=["https://fonts.googleapis.com/css?family=Inter"],
)
app.add_page(
    index,
    on_load=State.on_load,
    title="Customer Data App",
    description="A simple app to manage customer data.",
)
