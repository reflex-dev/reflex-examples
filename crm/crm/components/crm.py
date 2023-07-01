from crm.state import State
from crm.state.models import Contact
import reflex as rx


class CRMState(State):
    contacts: list[Contact] = []
    query = ""

    def get_contacts(self) -> list[Contact]:
        with rx.session() as sess:
            if self.query != "":
                print("Query...")
                self.contacts = (
                    sess.query(Contact)
                    .filter(Contact.user_email == self.user.email)
                    .filter(Contact.contact_name.contains(self.query))
                    .all()
                )
                return
            print("All...")
            self.contacts = (
                sess.query(Contact).filter(Contact.user_email == self.user.email).all()
            )

    def filter(self, query):
        self.query = query
        print("Returning...")
        return self.get_contacts()

    @rx.var
    def num_contacts(self):
        return len(self.contacts)


class AddModalState(CRMState):
    show: bool = False
    name: str = ""
    email: str = ""

    def toggle(self):
        self.show = not self.show

    def add_contact(self):
        if not self.user:
            raise ValueError("No user logged in")
        with rx.session() as sess:
            sess.expire_on_commit = False
            sess.add(
                Contact(
                    user_email=self.user.email, contact_name=self.name, email=self.email
                )
            )
            sess.commit()
            self.toggle()
            return self.get_contacts()


def add_modal():
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header("Add"),
                rx.modal_body(
                    rx.input(
                        on_change=AddModalState.set_name,
                        placeholder="Name",
                        margin_bottom="0.5rem",
                    ),
                    rx.input(on_change=AddModalState.set_email, placeholder="Email"),
                    padding_y=0,
                ),
                rx.modal_footer(
                    rx.button("Close", on_click=AddModalState.toggle),
                    rx.button(
                        "Add", on_click=AddModalState.add_contact, margin_left="0.5rem"
                    ),
                ),
            )
        ),
        is_open=AddModalState.show,
    )


def contact_row(
    contact,
):
    return rx.tr(
        rx.td(contact.contact_name),
        rx.td(contact.email),
        rx.td(rx.badge(contact.stage)),
    )


def crm():
    return rx.box(
        rx.button("Refresh", on_click=CRMState.get_contacts),
        rx.hstack(
            rx.heading("Contacts"),
            rx.button("Add", on_click=AddModalState.toggle),
            justify_content="space-between",
            align_items="flex-start",
            margin_bottom="1rem",
        ),
        rx.responsive_grid(
            rx.box(
                rx.stat(
                    rx.stat_label("Contacts"), rx.stat_number(CRMState.num_contacts)
                ),
                border="1px solid #eaeaef",
                padding="1rem",
                border_radius=8,
            ),
            columns=["5"],
            margin_bottom="1rem",
        ),
        add_modal(),
        rx.input(placeholder="Filter by name...", on_change=CRMState.filter),
        rx.table_container(
            rx.table(rx.tbody(rx.foreach(CRMState.contacts, contact_row))),
            margin_top="1rem",
        ),
        width="100%",
        max_width="960px",
        padding_x="0.5rem",
    )
