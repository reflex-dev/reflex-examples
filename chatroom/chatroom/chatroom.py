"""Reflex chatroom -- send server events to other sessions."""
import time
import typing as t

from rxconfig import config

import reflex as rx


class Message(rx.Base):
    nick: str
    sent: float
    message: str


class State(rx.State):
    nick: t.Optional[str] = ""
    nicks: t.List[str] = []
    messages: t.List[Message] = []
    in_message: str = ""

    def set_nicks(self, nicks: t.List[str]) -> None:
        """Set the list of nicks (from broadcast_nicks)."""
        self.nicks = nicks

    def incoming_message(self, message: Message) -> None:
        """Append incoming message to current message list."""
        self.messages.append(message)

    async def nick_change(self, nick: str) -> None:
        """Handle on_blur from nick text input."""
        self.nick = nick
        await broadcast_nicks()

    async def send_message(self) -> None:
        """Broadcast chat message to other connected clients."""
        m = Message(nick=self.nick, sent=time.time(), message=self.in_message)
        await broadcast_event("state.incoming_message", payload=dict(message=m))
        self.in_message = ""

    @rx.var
    def other_nicks(self) -> t.List[str]:
        """Filter nicks list to exclude nick from this instance."""
        return [n for n in self.nicks if n != self.nick]


def index() -> rx.Component:
    return rx.chakra.vstack(
        rx.chakra.center(rx.chakra.heading("Reflex Chat!", font_size="2em")),
        rx.chakra.hstack(
            rx.chakra.vstack(
                rx.chakra.input(
                    placeholder="Nick",
                    default_value=State.nick,
                    on_blur=State.nick_change,
                ),
                rx.chakra.text("Other Users", font_weight="bold"),
                rx.foreach(State.other_nicks, rx.chakra.text),
                width="20vw",
                align_items="left",
            ),
            rx.chakra.vstack(
                rx.foreach(
                    State.messages,
                    lambda m: rx.chakra.text("<", m.nick, "> ", m.message),
                ),
                rx.chakra.form(
                    rx.chakra.hstack(
                        rx.chakra.input(
                            placeholder="Message",
                            value=State.in_message,
                            on_change=State.set_in_message,
                            flex_grow=1,
                        ),
                        rx.chakra.button("Send", on_click=State.send_message),
                    ),
                    on_submit=lambda d: State.send_message(),
                ),
                width="60vw",
                align_items="left",
            ),
        ),
    )


app = rx.App()
app.add_page(index)


async def broadcast_event(name: str, payload: t.Dict[str, t.Any] = {}) -> None:
    """Simulate frontend event with given name and payload from all clients."""
    responses = []
    for state in app.state_manager.states.values():
        async for update in state._process(
            event=rx.event.Event(
                token=state.router.session.client_token,
                name=name,
                router_data=state.router_data,
                payload=payload,
            ),
        ):
            # Emit the event.
            responses.append(
                app.event_namespace.emit(
                    str(rx.constants.SocketEvent.EVENT),
                    update.json(),
                    to=state.router.session.session_id,
                ),
            )
    for response in responses:
        await response


async def broadcast_nicks() -> None:
    """Simulate State.set_nicks event with updated nick list from all clients."""
    nicks = []
    for state in app.state_manager.states.values():
        nicks.append(state.nick)
    await broadcast_event("state.set_nicks", payload=dict(nicks=nicks))
