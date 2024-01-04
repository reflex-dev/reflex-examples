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
            model="text-davinci-003",
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
    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.image(src="/favicon.ico", width="50px"),
                    rx.heading("Reflex | Personalized Sales", size="lg"),
                ),
                href="/",
            ),
            rx.menu(
                rx.menu_button(
                    "Menu", bg="black", color="white", border_radius="md", px=4, py=2
                ),
                rx.menu_list(
                    rx.link(
                        rx.menu_item(
                            rx.hstack(rx.text("Customers"), rx.icon(tag="hamburger"))
                        ),
                        href="/",
                    ),
                    rx.menu_divider(),
                    rx.link(
                        rx.menu_item(
                            rx.hstack(rx.text("Onboarding"), rx.icon(tag="add"))
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
    return rx.tr(
        rx.td(user.customer_name),
        rx.td(user.email),
        rx.td(user.age),
        rx.td(user.gender),
        rx.td(user.location),
        rx.td(user.job),
        rx.td(user.salary),
        rx.td(
            rx.button(
                "Delete",
                on_click=lambda: State.delete_customer(user.email),
                bg="red",
                color="white",
            )
        ),
        rx.td(
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
                ),
                bg="blue",
                color="white",
            )
        ),
    )


def add_customer():
    """Add a customer to the database."""
    return rx.center(
        rx.vstack(
            navbar(),
            rx.heading("Customer Onboarding"),
            rx.hstack(
                rx.vstack(
                    rx.input(placeholder="Input Name", on_blur=State.set_customer_name),
                    rx.input(placeholder="Input Email", on_blur=State.set_email),
                ),
                rx.vstack(
                    rx.input(placeholder="Input Location", on_blur=State.set_location),
                    rx.input(placeholder="Input Job", on_blur=State.set_job),
                ),
            ),
            rx.select(
                ["male", "female", "other"],
                placeholder="Select Gender",
                on_change=State.set_gender,
            ),
            rx.input(on_change=State.set_age, placeholder="Age"),
            rx.input(on_change=State.set_salary, placeholder="Salary"),
            rx.button_group(
                rx.button("Submit Customer", on_click=State.add_customer),
                rx.button(rx.icon(tag="hamburger"), on_click=State.customer_page),
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
    return rx.center(
        rx.vstack(
            navbar(),
            rx.vstack(
                rx.hstack(
                    rx.heading("Customers"),
                    rx.button(
                        rx.icon(tag="add"),
                        on_click=State.onboarding_page,
                        bg="#F7FAFC",
                        border="1px solid #ddd",
                    ),
                ),
                rx.table_container(
                    rx.table(
                        rx.thead(
                            rx.tr(
                                rx.th("Name"),
                                rx.th("Email"),
                                rx.th("Age"),
                                rx.th("Gender"),
                                rx.th("Location"),
                                rx.th("Job"),
                                rx.th("Salary"),
                                rx.th("Delete"),
                                rx.th("Generate Email"),
                            )
                        ),
                        rx.tbody(rx.foreach(State.get_users, show_customer)),
                    ),
                    bg="#F7FAFC ",
                    border="1px solid #ddd",
                    border_radius="25px",
                ),
                align_items="left",
                padding_top="7em",
            ),
            rx.vstack(
                rx.heading("Generated Email"),
                rx.cond(
                    State.gen_response,
                    rx.progress(is_indeterminate=True, color="blue", width="100%"),
                    rx.progress(value=0, width="100%"),
                ),
                rx.text_area(
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


# Add state and page to the app.
app = rx.App(state=State, admin_dash=rx.AdminDash(models=[Customer]))
app.add_page(index)
app.add_page(add_customer, "/onboarding")
