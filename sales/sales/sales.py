import pynecone as pc
import os
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"
products = {'T-shirt': {   'description': 'A plain white t-shirt made of 100% cotton.',   'price': 10.99   },   'Jeans': {   'description': 'A pair of blue denim jeans with a straight leg fit.',   'price': 24.99   },   'Hoodie': {   'description': 'A black hoodie made of a cotton and polyester blend.',   'price': 34.99   },   'Cardigan': {   'description': 'A grey cardigan with a V-neck and long sleeves.',   'price': 36.99   },   'Joggers': {   'description': 'A pair of black joggers made of a cotton and polyester blend.',   'price': 44.99   },   'Dress': {   'description': 'A black dress made of 100% polyester.',   'price': 49.99   },   'Jacket': {   'description': 'A navy blue jacket made of 100% cotton.',   'price': 55.99   },   'Skirt': {   'description': 'A brown skirt made of a cotton and polyester blend.',   'price': 29.99   },   'Shorts': {   'description': 'A pair of black shorts made of a cotton and polyester blend.',   'price': 19.99   },   'Sweater': {   'description': 'A white sweater with a crew neck and long sleeves.',   'price': 39.99}}


class Customer(pc.Model, table=True):
    """The customer model."""

    customer_name: str
    email: str
    age: int
    gender: str
    location: str
    job: str
    salary: int


class State(pc.State):
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
    response: str = ""
    gen_response = False

    def add_customer(self):
        """Add a customer to the database."""
        with pc.session() as session:
            if session.query(Customer).filter_by(email=self.email).first():
                return pc.window_alert("User already exists")
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
        return pc.window_alert(f"User {self.customer_name} has been added.")

    def customer_page(self):
        """The customer page."""
        return pc.redirect("/")
    
    def onboarding_page(self):
        """The onboarding page."""
        return pc.redirect("/onboarding")

    def delete_customer(self, email: str):
        """Delete a customer from the database."""
        with pc.session() as session:
            session.query(Customer).filter_by(email=email).delete()
            session.commit()

    def call_openai(
        self,
        name: str,
        email: str,
        age: int,
        gender: str,
        location: str,
        job: str,
        salary: int,
    ):
        """Call OpenAI to generate a personalized response."""
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Based on these {products} write a sales email to {name} adn email {email} who is {age} years old and a {gender} gender. {name} lives in {location} and works as a {job} and earns {salary} per year. Make sure the email reccomends one product only and is personalized to {name}. The company is named Pynecone its website is https://pynecone.io",
            temperature=0.7,
            max_tokens=2250,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        self.gen_response = False
        self.response = response.choices[0].text

    def send_email(
        self,
        name: str,
        email: str,
        age: int,
        gender: str,
        location: str,
        job: str,
        salary: int,
    ):
        """Call call_openai and set gen_response to True for progress bar."""
        self.gen_response = True
        return self.call_openai(name, email, age, gender, location, job, salary)

    @pc.var
    def get_users(self) -> list[Customer]:
        """Get all users from the database."""
        with pc.session() as session:
            self.users = session.query(Customer).all()
            return self.users


def navbar():
    """The navbar for the top of the page."""
    return pc.box(
        pc.hstack(
            pc.link(
                pc.hstack(
                    pc.image(src="/pinecone.ico", width="50px"),
                    pc.heading("Pynecone | Personalized Sales", size="lg"),
                ),
                href="https://pynecone.io",
            ),
            pc.menu(
                pc.menu_button(
                    "Menu", bg="black", color="white", border_radius="md", px=4, py=2
                ),
                pc.menu_list(
                    pc.link(
                        pc.menu_item(
                            pc.hstack(
                                pc.text("Customers"), pc.icon(tag="HamburgerIcon")
                            )
                        ),
                        href="/",
                    ),
                    pc.menu_divider(),
                    pc.link(
                        pc.menu_item(
                            pc.hstack(pc.text("Onboarding"), pc.icon(tag="AddIcon"))
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
    return pc.tr(
        pc.td(user.customer_name),
        pc.td(user.email),
        pc.td(user.age),
        pc.td(user.gender),
        pc.td(user.location),
        pc.td(user.job),
        pc.td(user.salary),
        pc.td(
            pc.button(
                "Delete",
                on_click=lambda: State.delete_customer(user.email),
                bg="red",
                color="white",
            )
        ),
        pc.td(
            pc.button(
                "Generate Email",
                on_click=lambda: State.send_email(
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
    return pc.center(
        pc.vstack(
            navbar(),
            pc.heading("Customer Onboarding"),
            pc.hstack(
                pc.vstack(
                    pc.input(placeholder="Input Name", on_blur=State.set_customer_name),
                    pc.input(placeholder="Input Email", on_blur=State.set_email),
                ),
                pc.vstack(
                    pc.input(placeholder="Input Location", on_blur=State.set_location),
                    pc.input(placeholder="Input Job", on_blur=State.set_job),
                ),
            ),
            pc.select(
                ["male", "female", "other"],
                placeholder="Select Gender",
                on_change=State.set_gender,
            ),
            pc.input(on_change=State.set_age, placeholder="Age"),
            pc.input(on_change=State.set_salary, placeholder="Salary"),
            pc.button_group(
                pc.button("Submit Customer", on_click=State.add_customer),
                pc.button(pc.icon(tag="HamburgerIcon"), on_click=State.customer_page),
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
    return pc.center(
        pc.vstack(
            navbar(),
            pc.vstack(
                pc.hstack(
                    pc.heading("Customers"),
                    pc.button(pc.icon(tag="AddIcon"), on_click=State.onboarding_page, bg="#F7FAFC", border="1px solid #ddd"),
                ),
                pc.table_container(
                    pc.table(
                        pc.thead(
                            pc.tr(
                                pc.th("Name"),
                                pc.th("Email"),
                                pc.th("Age"),
                                pc.th("Gender"),
                                pc.th("Location"),
                                pc.th("Job"),
                                pc.th("Salary"),
                                pc.th("Delete"),
                                pc.th("Generate Email"),
                            )
                        ),
                        pc.tbody(pc.foreach(State.get_users, show_customer)),
                    ),
                    bg="#F7FAFC ",
                    border="1px solid #ddd",
                    border_radius="25px",
                ),
                align_items="left",
                padding_top="7em",
            ),
            pc.vstack(
                pc.heading("Generated Email"),
                pc.cond(
                    State.gen_response,
                    pc.progress(is_indeterminate=True, color="blue", width="100%"),
                    pc.progress(value=0, width="100%"),
                ),
                pc.text_area(
                    value=State.response,
                    width="100%",
                    height="100%",
                    bg="white",
                    color="black",
                    placeholder="Response",
                    readonly=True,
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
app = pc.App(state=State)
app.add_page(index)
app.add_page(add_customer, "/onboarding")
app.compile()
