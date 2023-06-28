"""Pynecone chatroom -- send server events to other sessions."""
import time
import typing as t

from pcconfig import config

import pynecone as pc


class Message(pc.Base):
    nick: str
    sent: float
    message: str


class State(pc.State):
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

    @pc.var
    def other_nicks(self) -> t.List[str]:
        """Filter nicks list to exclude nick from this instance."""
        return [n for n in self.nicks if n != self.nick]


def index() -> pc.Component:
    return pc.vstack(
        pc.center(pc.heading("Pynecone Chat!", font_size="2em")),
        pc.hstack(
            pc.vstack(
                pc.input(
                    placeholder="Nick",
                    default_value=State.nick,
                    on_blur=State.nick_change,
                ),
                pc.text("Other Users", font_weight="bold"),
                pc.foreach(State.other_nicks, pc.text),
                width="20vw",
                align_items="left",
            ),
            pc.vstack(
                pc.foreach(
                    State.messages,
                    lambda m: pc.text("<", m.nick, "> ", m.message),
                ),
                pc.form(
                    pc.hstack(
                        pc.input(
                            placeholder="Message",
                            value=State.in_message,
                            on_change=State.set_in_message,
                            flex_grow=1,
                        ),
                        pc.button("Send", on_click=State.send_message),
                    ),
                    on_submit=State.send_message,
                ),
                width="60vw",
                align_items="left",
            ),
        ),
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.compile()


async def broadcast_event(name: str, payload: t.Dict[str, t.Any] = {}) -> None:
    """Simulate frontend event with given name and payload from all clients."""
    event_ns = app.sio.namespace_handlers["/event"]
    responses = []
    for state in app.state_manager.states.values():
        async for update in state._process(
            event=pc.event.Event(
                token=state.get_token(),
                name=name,
                router_data=state.router_data,
                payload=payload,
            ),
        ):
            # Emit the event.
            responses.append(
                event_ns.emit(
                    str(pc.constants.SocketEvent.EVENT), update.json(), to=state.get_sid()
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
