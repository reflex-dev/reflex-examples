import uuid
from typing import Any

import reflex as rx

from .models import Notification, Subscriber
from .push import push


class PushState(rx.State):
    browser_id: str = rx.LocalStorage()
    waiting_for_registration: bool = False
    my_sub: Subscriber | None
    other_subs: list[Subscriber] = []
    refreshing: bool = False

    def refresh(self):
        self.refreshing = True
        yield
        try:
            if not self.browser_id:
                self.browser_id = str(uuid.uuid4())
            with rx.session() as session:
                self.my_sub = session.exec(
                    Subscriber.select().where(Subscriber.browser_id == self.browser_id)
                ).one_or_none()
                self.other_subs = session.exec(
                    Subscriber.select().where(Subscriber.browser_id != self.browser_id)
                ).all()
        finally:
            self.refreshing = False
        if self.my_sub is not None and self.waiting_for_registration:
            self.waiting_for_registration = False
            return rx.toast.info("Registration successful")

    def set_sub_status(self, enabled: bool):
        with rx.session() as session:
            sub = session.exec(
                Subscriber.select().where(Subscriber.browser_id == self.browser_id)
            ).one_or_none()
            if sub is not None:
                sub.enabled = enabled
                session.commit()
        self.my_sub.enabled = enabled
        self.refresh()

    def do_push_all(self, form_data: dict[str, Any]):
        self.refresh()
        print("Pushing from ", self.browser_id)
        notification = Notification(**form_data)
        remove_subs = push(self.other_subs, notification)
        if remove_subs:
            self._remove_subs_by_auth_key(remove_subs)

    def _remove_subs_by_auth_key(self, auth_keys: list[str]):
        with rx.session() as session:
            for sub in session.exec(
                Subscriber.select().where(Subscriber.auth_key.in_(auth_keys))
            ).all():
                print(f"    Removing old unused key {sub.auth_key}")
                session.delete(sub)
            session.commit()
        self.refresh()