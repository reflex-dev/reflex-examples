import reflex as rx
from ..backend.backend import State, Customer
from ..components.form_field import form_field
from ..components.gender_badges import gender_badge


def _header_cell(text: str, icon: str):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )


def show_customer(user: Customer):
    """Show a customer in a table row."""
    return rx.table.row(
        rx.table.row_header_cell(user.customer_name),
        rx.table.cell(user.email),
        rx.table.cell(user.age),
        rx.table.cell(
            rx.match(
                user.gender,
                ("Male", gender_badge("Male")),
                ("Female", gender_badge("Female")),
                ("Other", gender_badge("Other")),
                gender_badge("Other"),
            )
        ),
        rx.table.cell(user.location),
        rx.table.cell(user.job),
        rx.table.cell(user.salary),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    (State.current_user.id == user.id),
                    rx.button(
                        rx.icon("mail-plus", size=22),
                        rx.text("Generate Email", size="3"),
                        color_scheme="blue",
                        on_click=State.generate_email(user),
                        loading=State.gen_response,
                    ),
                    rx.button(
                        rx.icon("mail-plus", size=22),
                        rx.text("Generate Email", size="3"),
                        color_scheme="blue",
                        on_click=State.generate_email(user),
                        disabled=State.gen_response,
                    ),
                ),
                update_customer_dialog(user),
                rx.icon_button(
                    rx.icon("trash-2", size=22),
                    on_click=lambda: State.delete_customer(getattr(user, "id")),
                    size="2",
                    variant="solid",
                    color_scheme="red",
                ),
                min_width="max-content",
            ),
        ),
        style={"_hover": {"bg": rx.color("accent", 2)}},
        align="center",
    )


def add_customer_button() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=26),
                rx.text("Add Customer", size="4", display=["none", "none", "block"]),
                size="3",
            ),
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="users", size=34),
                    color_scheme="blue",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Customer Onboarding",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Fill the form with the customer's info",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5em",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        rx.hstack(
                            # Name
                            form_field(
                                "Name",
                                "Customer Name",
                                "text",
                                "customer_name",
                                "user",
                            ),
                            # Location
                            form_field(
                                "Location",
                                "Customer Location",
                                "text",
                                "location",
                                "map-pinned",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.hstack(
                            # Email
                            form_field(
                                "Email", "user@reflex.dev", "email", "email", "mail"
                            ),
                            # Job
                            form_field(
                                "Job", "Customer Job", "text", "job", "briefcase"
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        # Gender
                        rx.vstack(
                            rx.hstack(
                                rx.icon("user-round", size=16, stroke_width=1.5),
                                rx.text("Gender"),
                                align="center",
                                spacing="2",
                            ),
                            rx.select(
                                ["Male", "Female", "Other"],
                                placeholder="Select Gender",
                                name="gender",
                                direction="row",
                                as_child=True,
                                required=True,
                                width="100%",
                            ),
                            width="100%",
                        ),
                        rx.hstack(
                            # Age
                            form_field(
                                "Age",
                                "Customer Age",
                                "number",
                                "age",
                                "person-standing",
                            ),
                            # Salary
                            form_field(
                                "Salary",
                                "Customer Salary",
                                "number",
                                "salary",
                                "dollar-sign",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        width="100%",
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
                        rx.form.submit(
                            rx.dialog.close(
                                rx.button("Submit Customer"),
                            ),
                            as_child=True,
                        ),
                        padding_top="2em",
                        spacing="3",
                        mt="4",
                        justify="end",
                    ),
                    on_submit=State.add_customer_to_db,
                    reset_on_submit=False,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="1.5em",
            border=f"2.5px solid {rx.color('accent', 7)}",
            border_radius="25px",
        ),
    )


def update_customer_dialog(user):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                rx.icon("square-pen", size=22),
                color_scheme="green",
                size="2",
                variant="solid",
                on_click=lambda: State.get_user(user),
            ),
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="square-pen", size=34),
                    color_scheme="blue",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Edit Customer",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Edit the customer's info",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5em",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        rx.hstack(
                            # Name
                            form_field(
                                "Name",
                                "Customer Name",
                                "text",
                                "customer_name",
                                "user",
                                user.customer_name,
                            ),
                            # Location
                            form_field(
                                "Location",
                                "Customer Location",
                                "text",
                                "location",
                                "map-pinned",
                                user.location,
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.hstack(
                            # Email
                            form_field(
                                "Email",
                                "user@reflex.dev",
                                "email",
                                "email",
                                "mail",
                                user.email,
                            ),
                            # Job
                            form_field(
                                "Job",
                                "Customer Job",
                                "text",
                                "job",
                                "briefcase",
                                user.job,
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        # Gender
                        rx.vstack(
                            rx.hstack(
                                rx.icon("user-round", size=16, stroke_width=1.5),
                                rx.text("Gender"),
                                align="center",
                                spacing="2",
                            ),
                            rx.select(
                                ["Male", "Female", "Other"],
                                default_value=user.gender,
                                name="gender",
                                direction="row",
                                as_child=True,
                                required=True,
                                width="100%",
                            ),
                            width="100%",
                        ),
                        rx.hstack(
                            # Age
                            form_field(
                                "Age",
                                "Customer Age",
                                "number",
                                "age",
                                "person-standing",
                                user.age.to(str),
                            ),
                            # Salary
                            form_field(
                                "Salary",
                                "Customer Salary",
                                "number",
                                "salary",
                                "dollar-sign",
                                user.salary.to(str),
                            ),
                            spacing="3",
                            width="100%",
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
                        rx.form.submit(
                            rx.dialog.close(
                                rx.button("Update Customer"),
                            ),
                            as_child=True,
                        ),
                        padding_top="2em",
                        spacing="3",
                        mt="4",
                        justify="end",
                    ),
                    on_submit=State.update_customer_to_db,
                    reset_on_submit=False,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="1.5em",
            border=f"2px solid {rx.color('accent', 7)}",
            border_radius="25px",
        ),
    )


def main_table():
    return rx.fragment(
        rx.flex(
            add_customer_button(),
            rx.spacer(),
            rx.hstack(
                rx.cond(
                    State.sort_reverse,
                    rx.icon(
                        "arrow-down-z-a",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        on_click=State.toggle_sort,
                    ),
                    rx.icon(
                        "arrow-down-a-z",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        on_click=State.toggle_sort,
                    ),
                ),
                rx.select(
                    [
                        "customer_name",
                        "email",
                        "age",
                        "gender",
                        "location",
                        "job",
                        "salary",
                    ],
                    placeholder="Sort By: Name",
                    size="3",
                    on_change=lambda sort_value: State.sort_values(sort_value),
                ),
                rx.input(
                    placeholder="Search here...",
                    size="3",
                    on_change=lambda value: State.filter_values(value),
                ),
                spacing="3",
                align="center",
            ),
            spacing="3",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Name", "square-user-round"),
                    _header_cell("Email", "mail"),
                    _header_cell("Age", "person-standing"),
                    _header_cell("Gender", "user-round"),
                    _header_cell("Location", "map-pinned"),
                    _header_cell("Job", "briefcase"),
                    _header_cell("Salary", "dollar-sign"),
                    _header_cell("Actions", "cog"),
                ),
            ),
            rx.table.body(rx.foreach(State.users, show_customer)),
            variant="surface",
            size="3",
            width="100%",
        ),
    )
