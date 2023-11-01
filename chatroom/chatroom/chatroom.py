"""Reflex chatroom -- send server events to other sessions."""
from contextlib import suppress
import time
import typing as t

import reflex as rx


class Message(rx.Base):
    nick: str
    sent: float
    message: str


class State(rx.State):
    nick: t.Optional[str] = ""
    nicks: t.List[str] = []
    messages: t.List[Message] = []

    def update_other_nick(self, new_nick: str, old_nick: str | None) -> None:
        """Update another user's nick (from broadcast_nicks)."""
        with suppress(ValueError):
            self.nicks.remove(old_nick)
        self.nicks.append(new_nick)
        self.nicks.sort()

    def incoming_message(self, message: Message) -> None:
        """Append incoming message to current message list."""
        message = Message(**message)
        if message.nick not in self.nicks:
            self.update_other_nick(message.nick, None)
        self.messages.append(message)

    async def nick_change(self, nick: str) -> None:
        """Handle on_blur from nick text input."""
        await broadcast_nicks(new_nick=nick, old_nick=self.nick)
        self.nick = nick

    async def send_message(self, form_data: dict[str, str]) -> None:
        """Broadcast chat message to other connected clients."""
        m = Message(nick=self.nick, sent=time.time(), message=form_data["in_message"])
        await broadcast_event("state.incoming_message", payload=dict(message=m))
        return rx.set_value("in_message", "")

    @rx.var
    def other_nicks(self) -> t.List[str]:
        """Filter nicks list to exclude nick from this instance."""
        return [n for n in self.nicks if n != self.nick]


def index() -> rx.Component:
    return rx.vstack(
        rx.center(rx.heading("Reflex Chat!", font_size="2em")),
        rx.hstack(
            rx.vstack(
                rx.input(
                    placeholder="Nick",
                    default_value=State.nick,
                    on_blur=State.nick_change,
                ),
                rx.text("Other Users", font_weight="bold"),
                rx.foreach(State.other_nicks, rx.text),
                width="20vw",
                align_items="left",
            ),
            rx.vstack(
                rx.foreach(
                    State.messages,
                    lambda m: rx.text("<", m.nick, "> ", m.message),
                ),
                rx.form(
                    rx.hstack(
                        rx.input(
                            placeholder="Message",
                            id="in_message",
                            flex_grow=1,
                        ),
                        rx.button("Send", type_="submit"),
                    ),
                    on_submit=State.send_message,
                ),
                width="60vw",
                align_items="left",
            ),
        ),
    )


# Add state and page to the app.
app = rx.App(state=State)
app.add_page(index)
app.compile()


async def broadcast_event(name: str, payload: t.Dict[str, t.Any] = {}) -> None:
    """Simulate frontend event with given name and payload from all clients."""
    await app.event_namespace.emit_update(
        rx.state.StateUpdate(
            events=[
                rx.event.Event(
                    token="<all>",
                    name=name,
                    router_data={},
                    payload=payload,
                ),
            ]
        ),
        sid=None,  # send to all connected clients
    )


async def broadcast_nicks(new_nick: str, old_nick: str) -> None:
    """Simulate State.set_nicks event with updated nick list from all clients."""
    await broadcast_event(
        "state.update_other_nick", payload=dict(new_nick=new_nick, old_nick=old_nick)
    )
