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
    return rx.chakra.modal(
        rx.chakra.modal_overlay(
            rx.chakra.modal_content(
                rx.chakra.modal_header("Add"),
                rx.chakra.modal_body(
                    rx.chakra.input(
                        on_change=AddModalState.set_name,
                        placeholder="Name",
                        margin_bottom="0.5rem",
                    ),
                    rx.chakra.input(on_change=AddModalState.set_email, placeholder="Email"),
                    padding_y=0,
                ),
                rx.chakra.modal_footer(
                    rx.chakra.button("Close", on_click=AddModalState.toggle),
                    rx.chakra.button(
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
    return rx.chakra.tr(
        rx.chakra.td(contact.contact_name),
        rx.chakra.td(contact.email),
        rx.chakra.td(rx.chakra.badge(contact.stage)),
    )


def crm():
    return rx.chakra.box(
        rx.chakra.button("Refresh", on_click=CRMState.get_contacts),
        rx.chakra.hstack(
            rx.chakra.heading("Contacts"),
            rx.chakra.button("Add", on_click=AddModalState.toggle),
            justify_content="space-between",
            align_items="flex-start",
            margin_bottom="1rem",
        ),
        rx.chakra.responsive_grid(
            rx.chakra.box(
                rx.chakra.stat(
                    rx.chakra.stat_label("Contacts"), rx.chakra.stat_number(CRMState.num_contacts)
                ),
                border="1px solid #eaeaef",
                padding="1rem",
                border_radius=8,
            ),
            columns=["5"],
            margin_bottom="1rem",
        ),
        add_modal(),
        rx.chakra.input(placeholder="Filter by name...", on_change=CRMState.filter),
        rx.chakra.table_container(
            rx.chakra.table(rx.chakra.tbody(rx.foreach(CRMState.contacts, contact_row))),
            margin_top="1rem",
        ),
        width="100%",
        max_width="960px",
        padding_x="0.5rem",
    )
