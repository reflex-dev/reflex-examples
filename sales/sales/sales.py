from openai import OpenAI

import reflex as rx
from sqlmodel import select

from .models import Customer

client = OpenAI()
products = {
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

    generate_email_data: dict = {}

    async def call_openai(self):
        name: str = self.generate_email_data["name"]
        email: str = self.generate_email_data["email"]
        age: int = self.generate_email_data["age"]
        gender: str = self.generate_email_data["gender"]
        location: str = self.generate_email_data["location"]
        job: str = self.generate_email_data["job"]
        salary: int = self.generate_email_data["salary"]
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Based on these {products} write a sales email to {name} adn email {email} who is {age} years old and a {gender} gender. {name} lives in {location} and works as a {job} and earns {salary} per year. Make sure the email reccomends one product only and is personalized to {name}. The company is named Reflex its website is https://reflex.dev",
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

    @rx.var
    def get_users(self) -> list[Customer]:
        """Get all users from the database."""
        with rx.session() as session:
            self.users = session.exec(select(Customer)).all()
            return self.users

    def open_text_area(self):
        self.text_area_disabled = False

    def close_text_area(self):
        self.text_area_disabled = True


def navbar():
    """The navbar for the top of the page."""
    return rx.chakra.box(
        rx.chakra.hstack(
            rx.chakra.link(
                rx.chakra.hstack(
                    rx.chakra.image(src="/favicon.ico", width="50px"),
                    rx.chakra.heading("Reflex | Personalized Sales", size="lg"),
                ),
                href="/",
            ),
            rx.chakra.menu(
                rx.chakra.menu_button(
                    "Menu", bg="black", color="white", border_radius="md", px=4, py=2
                ),
                rx.chakra.menu_list(
                    rx.chakra.link(
                        rx.chakra.menu_item(
                            rx.chakra.hstack(rx.chakra.text("Customers"), rx.chakra.icon(tag="hamburger"))
                        ),
                        href="/",
                    ),
                    rx.chakra.menu_divider(),
                    rx.chakra.link(
                        rx.chakra.menu_item(
                            rx.chakra.hstack(rx.chakra.text("Onboarding"), rx.chakra.icon(tag="add"))
                        ),
                        href="/onboarding",
                    ),
                ),
            ),
            justify="space-between",
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
    return rx.chakra.tr(
        rx.chakra.td(user.customer_name),
        rx.chakra.td(user.email),
        rx.chakra.td(user.age),
        rx.chakra.td(user.gender),
        rx.chakra.td(user.location),
        rx.chakra.td(user.job),
        rx.chakra.td(user.salary),
        rx.chakra.td(
            rx.chakra.button(
                "Delete",
                on_click=lambda: State.delete_customer(user.email),
                bg="red",
                color="white",
            )
        ),
        rx.chakra.td(
            rx.chakra.button(
                "Generate Email",
                on_click=State.generate_email(
                    user.customer_name,
                    user.email,
                    user.age,
                    user.gender,
                    user.location,
                    user.job,
                    user.salary,
                ),
                bg="blue",
                color="white",
            )
        ),
    )


def add_customer():
    """Add a customer to the database."""
    return rx.chakra.center(
        rx.chakra.vstack(
            navbar(),
            rx.chakra.heading("Customer Onboarding"),
            rx.chakra.hstack(
                rx.chakra.vstack(
                    rx.chakra.input(placeholder="Input Name", on_blur=State.set_customer_name),
                    rx.chakra.input(placeholder="Input Email", on_blur=State.set_email),
                ),
                rx.chakra.vstack(
                    rx.chakra.input(placeholder="Input Location", on_blur=State.set_location),
                    rx.chakra.input(placeholder="Input Job", on_blur=State.set_job),
                ),
            ),
            rx.chakra.select(
                ["male", "female", "other"],
                placeholder="Select Gender",
                on_change=State.set_gender,
            ),
            rx.chakra.input(on_change=State.set_age, placeholder="Age"),
            rx.chakra.input(on_change=State.set_salary, placeholder="Salary"),
            rx.chakra.button_group(
                rx.chakra.button("Submit Customer", on_click=State.add_customer),
                rx.chakra.button(rx.chakra.icon(tag="hamburger"), on_click=State.customer_page),
                is_attached=False,
                spacing=3,
            ),
            box_shadow="lg",
            bg="#F7FAFC ",
            padding="1em",
            border="1px solid #ddd",
            border_radius="25px",
        ),
        padding_top="10em",
    )


def index():
    """The main page."""
    return rx.chakra.center(
        rx.chakra.vstack(
            navbar(),
            rx.chakra.vstack(
                rx.chakra.hstack(
                    rx.chakra.heading("Customers"),
                    rx.chakra.button(
                        rx.chakra.icon(tag="add"),
                        on_click=State.onboarding_page,
                        bg="#F7FAFC",
                        border="1px solid #ddd",
                    ),
                ),
                rx.chakra.table_container(
                    rx.chakra.table(
                        rx.chakra.thead(
                            rx.chakra.tr(
                                rx.chakra.th("Name"),
                                rx.chakra.th("Email"),
                                rx.chakra.th("Age"),
                                rx.chakra.th("Gender"),
                                rx.chakra.th("Location"),
                                rx.chakra.th("Job"),
                                rx.chakra.th("Salary"),
                                rx.chakra.th("Delete"),
                                rx.chakra.th("Generate Email"),
                            )
                        ),
                        rx.chakra.tbody(rx.foreach(State.get_users, show_customer)),
                    ),
                    bg="#F7FAFC ",
                    border="1px solid #ddd",
                    border_radius="25px",
                ),
                align_items="left",
                padding_top="7em",
            ),
            rx.chakra.vstack(
                rx.chakra.heading("Generated Email"),
                rx.cond(
                    State.gen_response,
                    rx.chakra.progress(is_indeterminate=True, color="blue", width="100%"),
                    rx.chakra.progress(value=0, width="100%"),
                ),
                rx.chakra.text_area(
                    id="email_content",
                    is_disabled=State.gen_response,
                    on_blur=State.set_email_content_data,
                    width="100%",
                    height="100%",
                    bg="white",
                    color="black",
                    placeholder="Response",
                    min_height="20em",
                ),
                align_items="left",
                width="100%",
                padding_top="2em",
            ),
        ),
        padding="1em",
    )


app = rx.App(admin_dash=rx.AdminDash(models=[Customer]))
app.add_page(index)
app.add_page(add_customer, "/onboarding")
