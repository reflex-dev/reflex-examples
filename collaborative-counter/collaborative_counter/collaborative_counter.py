import pynecone as pc
import asyncio
import typing as t
# refer https://github.com/pynecone-io/pynecone/issues/438
class State(pc.State):
    counter: int = 0
    async def counter_up(self):
        self.counter = self.counter + 1
        await set_state_count(self.counter)

    async def counter_down(self):
        self.counter = self.counter - 1
        await set_state_count(self.counter)

    def set_counter(self, counter: t.SupportsInt) -> None:
        self.counter = counter
    async def counter_change(self, counter:t.SupportsInt) -> None:
        self.counter = counter
        await broadcast_counter()


async def broadcast_counter() -> None:
    """Simulate State.set_counter event with updated nick list from all clients."""
    counters = []
    for state in app.state_manager.states.values():
        counters.append(state.counter)
    await broadcast_event("state.set_counter", payload=dict(counter=counters))

async def broadcast_event(name: str, payload: t.Dict[str, t.Any] = {}) -> None:
    """Simulate frontend event with given name and payload from all clients."""
    event_ns = app.sio.namespace_handlers["/event"]
    responses = []
    for state in app.state_manager.states.values():
        update = await state._process(
            event=pc.event.Event(
                token=state.get_token(),
                name=name,
                router_data=state.router_data,
                payload=payload,
            ),
        )
        # Emit the event.
        responses.append(
            event_ns.emit(
                str(pc.constants.SocketEvent.EVENT), update.json(), to=state.get_sid()
            ),
        )
    for response in responses:
        await response
    
        
def index():
    return pc.center(
        pc.vstack(
            pc.heading("Counter", 
                font_size="2em", 
                background_image="linear-gradient(271.68deg, #211344 25%, #443213 50% )",
                background_clip="text",
            ),
            pc.hstack(
                pc.button("+", 
                    border="0.15em solid",
                    on_click=State.counter_up,
                    border_radius="0.5em",
                    padding="0.5em",
                    _hover={
                        "color": "rgb(107,99,246)",
                    },
                ),
 
                pc.button("-", 
                    border="0.15em solid",
                    on_click=State.counter_down,
                    border_radius="0.5em",
                    padding="0.5em",
                    _hover={
                        "color": "rgb(107,99,246)",
                    },
                ),
            ),
            pc.link(
                State.counter,
                href="#",
                border="0.1em solid",
                padding="0.1em",
                border_radius="0.5em",
                _hover={
                    "color": "rgb(107,99,246)",
                },
                font_size=["2em", "3em", "3em", "4em"],
                font_weight=800,
                font_family="Inter",
                background_image="linear-gradient(271.68deg, #EE756A 25%, #756AEE 50%)",
                background_clip="text",
            ),
            spacing="1.5em",
            font_size="2em",
        ),
        padding_top="10%",
    )



async def set_state_count(count_val:int):
    print("count_val = "+str(count_val))
    keys = list(app.state_manager.states) #convert the keys of dict into the list
    ret_count_val: int = count_val
    for token in keys: # change state.count for all current running frontend
        state = app.state_manager.get_state(token)
        state.counter = count_val
        app.state_manager.set_state(token, state)
    return {"state_count":ret_count_val}

meta = [
    {"name": "theme_color", "content": "#FFFFFF"},
    {"char_set": "UTF-8"},
    {"property": "og:url", "content": "url"},
]
# Add state and page to the app.
app = pc.App(state=State)
app.add_page(
    index,
    meta=meta,
    title="Collaborative Counter App",
    description="A collaborative counter app",    
    )
app.api.add_api_route("/state_count/{count_val}", set_state_count)
app.compile()
