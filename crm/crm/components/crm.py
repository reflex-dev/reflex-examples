from crm.state import State
from crm.state.models import Contact
import pynecone as pc


class CRMState(State):
    contacts: list[Contact] = []
    query = ""

    def get_contacts(self) -> list[Contact]:
        if not self.user:
            return
        with pc.session() as sess:
            if self.query != "":
                self.contacts = (
                    sess.query(Contact)
                    .filter(Contact.user_email == self.user.email)
                    .filter(Contact.contact_name.contains(self.query))
                    .all()
                )
                return
            self.contacts = (
                sess.query(Contact).filter(Contact.user_email == self.user.email).all()
            )

    def filter(self, query):
        self.query = query
        return self.get_contacts()

    @pc.var
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
        with pc.session() as sess:
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
    return pc.modal(
        pc.modal_overlay(
            pc.modal_content(
                pc.modal_header("Add"),
                pc.modal_body(
                    pc.input(
                        on_change=AddModalState.set_name,
                        placeholder="Name",
                        margin_bottom="0.5rem",
                    ),
                    pc.input(on_change=AddModalState.set_email, placeholder="Email"),
                    padding_y=0,
                ),
                pc.modal_footer(
                    pc.button("Close", on_click=AddModalState.toggle),
                    pc.button(
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
    return pc.tr(
        pc.td(contact.contact_name),
        pc.td(contact.email),
        pc.td(pc.badge(contact.stage)),
    )


def crm():
    return pc.box(
        pc.hstack(
            pc.heading("Contacts"),
            pc.button("Add", on_click=AddModalState.toggle),
            justify_content="space-between",
            align_items="flex-start",
            margin_bottom="1rem",
        ),
        pc.responsive_grid(
            pc.box(
                pc.stat(
                    pc.stat_label("Contacts"), pc.stat_number(CRMState.num_contacts)
                ),
                border="1px solid #eaeaef",
                padding="1rem",
                border_radius=8,
            ),
            columns=["5"],
            margin_bottom="1rem",
        ),
        add_modal(),
        pc.input(placeholder="Filter by name...", on_change=CRMState.filter),
        pc.table_container(
            pc.table(pc.tbody(pc.foreach(CRMState.contacts, contact_row))),
            margin_top="1rem",
        ),
        width="100%",
        max_width="960px",
        padding_x="0.5rem",
    )
