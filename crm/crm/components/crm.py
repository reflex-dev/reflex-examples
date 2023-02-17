from crm.state import State
from crm.state.models import Contact, STAGES
from typing import Optional
import pynecone as pc


class CRMState(State):
    contacts: list[Contact] = []
    query = ""
    stage = STAGES[0]
    detail: Optional[Contact] = None

    def get_contacts(self) -> list[Contact]:
        if not self.user:
            return
        with pc.session() as sess:
            if self.query != "":
                self.contacts = (
                    sess.query(Contact)
                    .filter(Contact.user_email == self.user.email)
                    .filter(Contact.stage == self.stage)
                    .filter(Contact.contact_name.contains(self.query))
                    .all()
                )
                return
            self.contacts = (
                sess.query(Contact).filter(Contact.user_email == self.user.email).filter(Contact.stage == self.stage).all()
            )

    def filter(self, query):
        self.query = query
        return self.get_contacts()

    def set_stage(self, stage):
        self.stage = stage
        return self.get_contacts()
    
    def convert(self, contact):
        with pc.session() as sess:
            contact = sess.query(Contact).filter(Contact.id == contact["id"]).first()
            curr_stage_idx = STAGES.index(contact.stage)
            next_stage_idx = (curr_stage_idx + 1) % len(STAGES)
            contact.stage = STAGES[next_stage_idx]
            sess.commit()
        return self.get_contacts()
    
    def select_detail(self, contact):
        self.detail = contact

    @pc.var
    def num_contacts(self):
        return len(self.contacts)
    
    @pc.var
    def detail_selected(self) -> bool:
        return self.detail != None


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
            self.show = not self.show
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
        pc.td(pc.box(pc.icon(tag="ViewIcon")), on_click=lambda: CRMState.select_detail(contact), cursor="pointer"),
        pc.td(contact.contact_name),
        pc.td(contact.email),
        pc.td(pc.badge(contact.stage)),
        pc.td(pc.button("Convert", on_click=lambda: CRMState.convert(contact))),
    )


def crm():
    return pc.box(
        pc.hstack(
            pc.heading("Dashboard"),
            pc.hstack(
                pc.box(align_self="stretch", border_left="1px solid #eee", margin_right="1rem"),
                pc.box(CRMState.num_contacts, " contacts", padding_x="1rem", font_weight="500"),
                pc.button("Add", on_click=AddModalState.toggle),
            ),
            justify_content="space-between",
            align_items="flex-start",
            margin_bottom="1rem",
        ),
        add_modal(),
        pc.hstack(
            pc.input(placeholder="Filter by name...", default_value=CRMState.query, on_change=CRMState.filter),
            pc.select(STAGES, default_value=CRMState.stage, on_change=CRMState.set_stage)
        ),
        pc.table_container(
            pc.table(pc.tbody(pc.foreach(CRMState.contacts, contact_row))),
            margin_top="1rem",
            border="1px solid #eaeaef",
        ),
        pc.drawer(
            pc.drawer_overlay(
                pc.drawer_content(
                    pc.cond(CRMState.detail_selected,
                        pc.fragment(
                            pc.drawer_header(CRMState.detail.contact_name),
                            pc.drawer_body(
                                pc.box(CRMState.detail.email),
                                pc.box(pc.badge(CRMState.detail.stage))
                            ),
                        ),
                        pc.box()
                    ),
                    pc.drawer_footer(
                        pc.button(
                            "Close", on_click=lambda: CRMState.set_detail(None)
                        )
                    ),
                )
            ),
            is_open=CRMState.detail_selected,
        ),
        width="100%",
        max_width="960px",
        padding_x="0.5rem",
    )
