from crm.state import State
from crm.state.models import Contact
import reflex as rx
import reflex.components.radix.themes as rdxt


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
    return rdxt.dialog_root(
        rdxt.dialog_trigger(
            rdxt.button("Add", on_click=AddModalState.toggle),
            margin_bottom="1rem",
        ),
        rdxt.dialog_content(
            rdxt.dialog_title("Add"),
            rdxt.textfield_input(
                on_change=AddModalState.set_name,
                placeholder="Name",
                margin_bottom="0.5rem",
            ),
            rdxt.textfield_input(
                on_change=AddModalState.set_email, placeholder="Email"
            ),
            rdxt.dialog_close(
                rdxt.button("Close", on_click=AddModalState.toggle),
            ),
            rdxt.button(
                "Add", on_click=AddModalState.add_contact, margin_left="0.5rem"
            ),
        ),
    )


def contact_row(
    contact,
):
    return rdxt.table_row(
        rdxt.table_cell(contact.contact_name),
        rdxt.table_cell(contact.email),
        rdxt.table_cell(rdxt.badge(contact.stage)),
    )


def crm():
    return rdxt.box(
        rdxt.button("Refresh", on_click=CRMState.get_contacts),
        rx.hstack(
            rdxt.heading("Contacts"),
            add_modal(),
            #             rdxt.button("Add", on_click=AddModalState.toggle),
            justify_content="space-between",
            align_items="flex-start",
            margin_bottom="1rem",
        ),
        rx.chakra.responsive_grid(
            rdxt.box(
                rx.chakra.stat(number=CRMState.num_contacts, label="Contacts"),
                border="1px solid #eaeaef",
                padding="1rem",
                border_radius=8,
            ),
            columns=["5"],
            margin_bottom="1rem",
        ),
        rdxt.textfield_input(
            placeholder="Filter by name...", on_change=CRMState.filter
        ),
        rdxt.table_root(
            rdxt.table_body(
                rx.foreach(CRMState.contacts, contact_row),
            )
        ),
        width="100%",
        max_width="960px",
        padding_x="0.5rem",
    )
