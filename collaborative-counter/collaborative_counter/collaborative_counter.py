import pynecone as pc
import asyncio
from .styles import base_style

async def set_state_count(count_val:int):
    keys = list(app.state_manager.states) #convert the keys of dict into the list
    ret_count_val: int = count_val
    for token in keys: # change state.count for all current running frontend
        state = app.state_manager.get_state(token)
        state.count = count_val
        app.state_manager.set_state(token, state)
    return {"state_count":ret_count_val}


class State(pc.State):
    count: int = 0
    is_run_tick:bool = False
    async def count_up(self):
        self.count = self.count + 1
        await set_state_count(self.count)

    async def count_down(self):
        self.count = self.count - 1
        await set_state_count(self.count)
        
    async def tick(self):
        # run tick for update frontend ui for updating count
        if self.is_run_tick:
            await asyncio.sleep(0.5)
            return self.tick
        
    async def onload(self):
        self.is_run_tick = True
        return self.tick
    
        
def index():
    return pc.center(
        pc.vstack(
            pc.heading("Counter"),
            pc.text("Collaborative Count"),
            pc.hstack(
                pc.button("+", on_click=State.count_up),
                pc.button("-", on_click=State.count_down),
            ),
            pc.link(State.count),
            spacing="1.5em",
            font_size="2em",
        ),
        padding_top="10%",
    )

print("Hint:You can open http://localhost:8000/state_count/33 to set count value as 33")
# Add state and page to the app.

app = pc.App(state=State, style=base_style)
app.api.add_api_route("/state_count/{count_val}", set_state_count)
app.add_page(
    index,
    title = "Collaborative Counter App",
    description = "A collaborative counter app",
    meta = [
        {"name": "theme_color", "content": "#FFFFFF"},
        {"char_set": "UTF-8"},
        {"property": "og:url", "content": "url"},
    ],
    on_load = State.onload,
)
app.compile()
