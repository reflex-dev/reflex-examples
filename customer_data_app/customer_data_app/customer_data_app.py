"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from sqlmodel import select, asc, or_, func

import reflex as rx


class Customer(rx.Model, table=True):
    """The customer model."""

    name: str
    email: str
    phone: str
    address: str


class State(rx.State):
    """The app state."""

    users: list[Customer] = []
    sort_value: str = ""
    search_value: str = ""
    num_users: int
    current_user: Customer = Customer()

    def handle_add_submit(self, form_data: dict):
        """Handle the form submit."""
        self.current_user = form_data

    def handle_update_submit(self, form_data: dict):
        """Handle the form submit."""
        self.current_user.update(form_data)

    def load_entries(self) -> list[Customer]:
        """Get all users from the database."""
        with rx.session() as session:
            query = select(Customer)

            if self.search_value != "":
                search_value = f"%{self.search_value.lower()}%"
                query = query.where(
                    or_(
                        *[
                            getattr(Customer, field).ilike(search_value)
                            for field in Customer.get_fields()
                        ],
                    )
                )

            if self.sort_value != "":
                sort_column = getattr(Customer, self.sort_value)
                order = asc(func.lower(sort_column))
                query = query.order_by(order)

            self.users = session.exec(query).all()
            self.num_users = len(self.users)

    def sort_values(self, sort_value: str):
        self.sort_value = sort_value
        self.load_entries()

    def filter_values(self, search_value):
        self.search_value = search_value
        self.load_entries()

    def get_user(self, user: Customer):
        self.current_user = user

    def add_customer_to_db(self):
        """Add a customer to the database."""
        with rx.session() as session:
            if session.exec(
                select(Customer).where(Customer.email == self.current_user["email"])
            ).first():
                return rx.window_alert("User with this email already exists")
            session.add(Customer(**self.current_user))
            session.commit()
        self.load_entries()
        return rx.window_alert(f"User {self.current_user["name"]} has been added.")

    def update_customer_to_db(self):
        """Update a customer in the database."""
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

    def delete_customer(self, id: int):
        """Delete a customer from the database."""
        with rx.session() as session:
            customer = session.exec(select(Customer).where(Customer.id == id)).first()
            session.delete(customer)
            session.commit()
        self.load_entries()


def add_fields(field):
    return rx.flex(
        rx.text(
            field,
            as_="div",
            size="2",
            mb="1",
            weight="bold",
        ),
        rx.input(
            placeholder=field,
            name=field,
        ),
        direction="column",
        spacing="2",
    )


def update_fields_and_attrs(field, attr):
    return rx.flex(
        rx.text(
            field,
            as_="div",
            size="2",
            mb="1",
            weight="bold",
        ),
        rx.input(
            placeholder=attr,
            name=field,
            default_value=attr,
        ),
        direction="column",
        spacing="2",
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
            rx.form(
                rx.flex(
                    # this is a list comprehension that passes each field in the Customer model to the add_fields function unless the field is "id"
                    *[
                        add_fields(field)
                        for field in Customer.get_fields()
                        if field != "id"
                    ],
                    rx.box(
                        rx.button(
                            "Submit",
                            type="submit",
                        ),
                    ),
                    direction="column",
                    spacing="3",
                ),
                on_submit=State.handle_add_submit,
                reset_on_submit=True,
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
                        on_click=State.add_customer_to_db,
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
                bg="red",
                color="white",
                on_click=lambda: State.get_user(user),
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
            rx.form(
                rx.flex(
                    *[
                        update_fields_and_attrs(
                            field, getattr(State.current_user, field)
                        )
                        for field in Customer.get_fields()
                        if field != "id"
                    ],
                    rx.box(
                        rx.button(
                            "Submit",
                            type="submit",
                        ),
                    ),
                    direction="column",
                    spacing="3",
                ),
                on_submit=State.handle_update_submit,
                reset_on_submit=True,
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
                        on_click=State.update_customer_to_db,
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


def show_customer(user: Customer):
    """Show a customer in a table row."""
    return rx.table.row(
        rx.table.cell(rx.avatar(fallback="DA")),
        *[
            rx.table.cell(getattr(user, field))
            for field in Customer.get_fields()
            if field != "id"
        ],
        rx.table.cell(
            update_customer(user),
        ),
        rx.table.cell(
            rx.button(
                "Delete",
                on_click=lambda: State.delete_customer(getattr(user, "id")),
                bg="red",
                color="white",
            ),
        ),
    )


def content():
    return rx.fragment(
        rx.vstack(
            rx.divider(),
            rx.hstack(
                rx.heading(
                    f"Total: {State.num_users} Customers",
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
                rx.input(
                    placeholder="Search here...",
                    on_change=lambda value: State.filter_values(value),
                ),
                width="100%",
                padding_x="2em",
                padding_top="2em",
                padding_bottom="1em",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("icon"),
                        # this is a list comprehension that passes each field in the Customer model to the column_header_cell function unless the field is "id"
                        *[
                            rx.table.column_header_cell(field)
                            for field in Customer.get_fields()
                            if field != "id"
                        ],
                        rx.table.column_header_cell("edit"),
                        rx.table.column_header_cell("delete"),
                    ),
                ),
                rx.table.body(rx.foreach(State.users, show_customer)),
                size="3",
                width="100%",
                on_mount=State.load_entries,
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
    #on_load=State.on_load,
    title="Customer Data App",
    description="A simple app to manage customer data.",
)
