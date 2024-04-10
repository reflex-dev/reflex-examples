from openai import OpenAI

import reflex as rx
from sqlmodel import select

from .models import Customer


products: dict[str, dict] = {
    "T-shirt": {
        "description": "A plain white t-shirt made of 100% cotton.",
        "price": 10.99,
    },
    "Jeans": {
        "description": "A pair of blue denim jeans with a straight leg fit.",
        "price": 24.99,
    },
    "Hoodie": {
        "description": "A black hoodie made of a cotton and polyester blend.",
        "price": 34.99,
    },
    "Cardigan": {
        "description": "A grey cardigan with a V-neck and long sleeves.",
        "price": 36.99,
    },
    "Joggers": {
        "description": "A pair of black joggers made of a cotton and polyester blend.",
        "price": 44.99,
    },
    "Dress": {"description": "A black dress made of 100% polyester.", "price": 49.99},
    "Jacket": {
        "description": "A navy blue jacket made of 100% cotton.",
        "price": 55.99,
    },
    "Skirt": {
        "description": "A brown skirt made of a cotton and polyester blend.",
        "price": 29.99,
    },
    "Shorts": {
        "description": "A pair of black shorts made of a cotton and polyester blend.",
        "price": 19.99,
    },
    "Sweater": {
        "description": "A white sweater with a crew neck and long sleeves.",
        "price": 39.99,
    },
}


class State(rx.State):
    """The app state."""

    customer_name: str = ""
    email: str = ""
    age: int = 0
    gender: str = "Other"
    location: str = ""
    job: str = ""
    salary: int = 0
    users: list[Customer] = []
    products: dict[str, str] = {}
    email_content_data: str = ""
    gen_response = False
    users: list[Customer] = []

    def add_customer(self):
        """Add a customer to the database."""
        with rx.session() as session:
            if session.exec(
                select(Customer).where(Customer.email == self.email)
            ).first():
                return rx.window_alert("User already exists")
            session.add(
                Customer(
                    customer_name=self.customer_name,
                    email=self.email,
                    age=self.age,
                    gender=self.gender,
                    location=self.location,
                    job=self.job,
                    salary=self.salary,
                )
            )
            session.commit()
        self.get_users()
        return rx.window_alert(f"User {self.customer_name} has been added.")

    def customer_page(self):
        """The customer page."""
        return rx.redirect("/")

    def onboarding_page(self):
        """The onboarding page."""
        return rx.redirect("/onboarding")

    def delete_customer(self, email: str):
        """Delete a customer from the database."""
        with rx.session() as session:
            customer = session.exec(
                select(Customer).where(Customer.email == email)
            ).first()
            session.delete(customer)
            session.commit()
        self.get_users()

    generate_email_data: dict = {}

    async def call_openai(self):
        name: str = self.generate_email_data["name"]
        email: str = self.generate_email_data["email"]
        age: int = self.generate_email_data["age"]
        gender: str = self.generate_email_data["gender"]
        location: str = self.generate_email_data["location"]
        job: str = self.generate_email_data["job"]
        salary: int = self.generate_email_data["salary"]
        response = OpenAI().completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Based on these {products} write a sales email to {name} and email {email} who is {age} years old and a {gender} gender. {name} lives in {location} and works as a {job} and earns {salary} per year. Make sure the email recommends one product only and is personalized to {name}. The company is named Reflex its website is https://reflex.dev",
            temperature=0.7,
            max_tokens=2250,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        self.gen_response = False
        # save the data related to email_content
        self.email_content_data = response.choices[0].text
        # update layout of email_content manually
        return rx.set_value("email_content", self.email_content_data)

    def generate_email(
        self,
        name: str,
        email: str,
        age: int,
        gender: str,
        location: str,
        job: str,
        salary: int,
    ):
        self.generate_email_data["name"] = name
        self.generate_email_data["email"] = email
        self.generate_email_data["age"] = age
        self.generate_email_data["gender"] = gender
        self.generate_email_data["location"] = location
        self.generate_email_data["job"] = job
        self.generate_email_data["salary"] = salary
        self.text_area_disabled = True
        self.gen_response = True
        return State.call_openai

    def get_users(self):
        """Get all users from the database."""
        with rx.session() as session:
            self.users = session.exec(select(Customer)).all()

    def open_text_area(self):
        self.text_area_disabled = False

    def close_text_area(self):
        self.text_area_disabled = True


def navbar():
    """The navbar for the top of the page."""
    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.image(src="/logo.jpg", width="50px"),
                    rx.heading("Reflex | Personalized Sales", size="8"),
                    align="center",
                ),
                href="/",
            ),
            rx.spacer(width="100%"),
            rx.menu.root(
                rx.menu.trigger(
                    rx.button("Menu", size="3"),
                    radius="md",
                ),
                rx.menu.content(
                    rx.menu.item(
                        rx.link(
                            rx.hstack("Customers", rx.icon(tag="menu")),
                            href="/",
                        ),
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        rx.link(
                            rx.hstack("Onboarding", rx.icon(tag="plus")),
                            href="/onboarding",
                        ),
                    ),
                    align="start",
                ),
            ),
            align="center",
            justify="center",
            border_bottom="0.2em solid #F0F0F0",
            padding_x="2em",
            padding_y="1em",
            bg="rgba(255,255,255, 0.97)",
        ),
        position="fixed",
        width="100%",
        top="0px",
        z_index="500",
    )


def show_customer(user: Customer):
    """Show a customer in a table row."""
    return rx.table.row(
        rx.table.row_header_cell(user.customer_name),
        rx.table.cell(user.email),
        rx.table.cell(user.age),
        rx.table.cell(user.gender),
        rx.table.cell(user.location),
        rx.table.cell(user.job),
        rx.table.cell(user.salary),
        rx.table.cell(
            rx.button(
                "Delete",
                on_click=lambda: State.delete_customer(user.email),  # type: ignore
                bg="red",
            )
        ),
        rx.table.cell(
            rx.button(
                "Generate Email",
                on_click=State.generate_email(
                    user.customer_name,
                    user.email,
                    user.age,
                    user.gender,
                    user.location,
                    user.job,
                    user.salary,
                ),  # type: ignore
                bg="blue",
            )
        ),
        align="center",
    )


def add_customer():
    """Add a customer to the database."""
    return rx.center(
        rx.vstack(
            navbar(),
            rx.heading("Customer Onboarding"),
            rx.hstack(
                rx.vstack(
                    rx.input(placeholder="Input Name", on_blur=State.set_customer_name),  # type: ignore
                    rx.input(placeholder="Input Email", on_blur=State.set_email),  # type: ignore
                ),
                rx.vstack(
                    rx.input(placeholder="Input Location", on_blur=State.set_location),  # type: ignore
                    rx.input(placeholder="Input Job", on_blur=State.set_job),  # type: ignore
                ),
            ),
            rx.select(
                ["male", "female", "other"],
                placeholder="Select Gender",
                on_change=State.set_gender,  # type: ignore
                width="100%",
            ),
            rx.input.root(
                rx.input.input(on_change=State.set_age, placeholder="Age"),  # type: ignore
                width="100%",
            ),
            rx.input.root(
                rx.input.input(on_change=State.set_salary, placeholder="Salary"),  # type: ignore
                width="100%",
            ),
            rx.hstack(
                rx.button("Submit Customer", on_click=State.add_customer),
                rx.button(rx.icon(tag="menu"), on_click=State.customer_page),
                spacing="3",
            ),
            align="center",
            class_name="shadow-lg",
            bg="#F7FAFC ",
            padding="1em",
            border="1px solid #ddd",
            border_radius="25px",
            spacing="3",
        ),
        padding_top="10em",
    )


def index():
    """The main page."""
    return rx.cond(
        State.is_hydrated,
        rx.center(
            navbar(),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Customers", size="8"),
                        rx.button(
                            rx.icon(tag="plus"),
                            on_click=State.onboarding_page,
                            size="3",
                        ),
                        align="center",
                    ),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Name"),
                                rx.table.column_header_cell("Email"),
                                rx.table.column_header_cell("Age"),
                                rx.table.column_header_cell("Gender"),
                                rx.table.column_header_cell("Location"),
                                rx.table.column_header_cell("Job"),
                                rx.table.column_header_cell("Salary"),
                                rx.table.column_header_cell("Delete"),
                                rx.table.column_header_cell("Generate Email"),
                            )
                        ),
                        rx.table.body(rx.foreach(State.users, show_customer)),  # type: ignore
                        variant="surface",
                        bg="#F7FAFC ",
                        border="1px solid #ddd",
                        border_radius="10px",
                    ),
                    align_items="left",
                    padding_top="7em",
                ),
                rx.vstack(
                    rx.heading("Generated Email", size="8"),
                    rx.cond(
                        State.gen_response,
                        rx.chakra.progress(
                            is_indeterminate=True, color="blue", width="100%"
                        ),
                        rx.chakra.progress(value=0, width="100%"),
                    ),
                    rx.text_area(
                        id="email_content",
                        is_disabled=State.gen_response,
                        on_blur=State.set_email_content_data,  # type: ignore
                        width="100%",
                        height="100%",
                        bg="white",
                        placeholder="Response",
                        min_height="20em",
                    ),
                    align_items="left",
                    width="100%",
                    padding_top="2em",
                ),
                padding_top="4em",
            ),
            padding="1em",
        ),
    )


app = rx.App(
    admin_dash=rx.AdminDash(models=[Customer]),
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="gray"
    ),
)
app.add_page(index, on_load=State.get_users)
app.add_page(add_customer, "/onboarding")
