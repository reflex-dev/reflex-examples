import reflex as rx
import asyncio
import random

N = 19 # There is a N*N grid for ground of snake
COLOR_NONE="#EEEEEE"
COLOR_BODY="#008800"
COLOR_FOOD="#FF00FF"
HEAD_U = "U"
HEAD_D = "D"
HEAD_L = "L"
HEAD_R = "R"

class State(rx.State):
    tmpdir:str = HEAD_R
    dir:str = HEAD_R # direction of what head of snake face
    snake:list[list[int]] = [[10,10], [10,11],[10,12],[10,13],[10,14],[10,15]] # all (X,Y) for snake's body  
    food:list[int] = [5,5] # X, Y of food
    cells:list[str] = (N*N)*[COLOR_NONE]
    tick_cnt:int = 1
    score: int = 0
    magic:int = 1
    rate:int = 10
    start: bool = False
    def turnOnTick(self):
        self.start = True
        if self.start:
            #print(self.snake)
            #print(self.food)
            return State.tick

    def turnOffTick(self):
        self.start = False
        if self.start:
            return State.tick
    def flip_switch(self, start):
        self.start = start
        if self.start:
            return State.tick

    async def tick(self):
        if self.start:
            await asyncio.sleep(0.5)
            self.dir = self.tmpdir
            head = self.snake[-1].copy()
            if(self.dir==HEAD_U):
                head[1] += (N-1)
                head[1] %= N
            elif(self.dir==HEAD_D):
                head[1] += (N+1)
                head[1] %= N
            elif(self.dir==HEAD_L):
                head[0] += (N-1)
                head[0] %= N
            elif(self.dir==HEAD_R):
                head[0] += (N+1)
                head[0] %= N
            if(head in self.snake):
                self.start = False
                self.magic = 1
                for i in range(N*N):
                    self.cells[i] = COLOR_NONE
                self.snake = [[10,10], [10,11],[10,12],[10,13],[10,14],[10,15]].copy()
                self.food = [5,5]
                self.dir = HEAD_R
                await asyncio.sleep(3)
                return State.tick

            self.cells[head[0]+ N*head[1]] = COLOR_BODY
            self.snake.append(head.copy())
            FOOD_EATEN = False
            while(self.food in self.snake):
                FOOD_EATEN = True
                self.food = [random.randint(0,N-1), random.randint(0,N-1)]
            self.cells[self.food[0]+ N*self.food[1]] = COLOR_FOOD
            if(FOOD_EATEN==False):
                self.cells[self.snake[0][0]+ N*self.snake[0][1]] = COLOR_NONE
                del self.snake[0]
            else:
                self.score+=self.magic
                self.magic += 1
                #self.rate = (int)(100*((float)self.score / (float)self.tick_cnt))
                self.rate = (int)(100*((float)(self.score)/(float)(self.tick_cnt)))
            self.tick_cnt += 1
            #print(self.tick_cnt)
            
            return State.tick

    def arrow_up(self):
        if(self.dir != HEAD_D):
            self.tmpdir = HEAD_U
        return
    def arrow_left(self):
        if(self.dir != HEAD_R):
            self.tmpdir = HEAD_L
        return
    def arrow_right(self):
        if(self.dir != HEAD_L):
            self.tmpdir = HEAD_R
        return
    def arrow_down(self):
        if(self.dir != HEAD_U):
            self.tmpdir = HEAD_D
        return
    def arrow_none(self):
        return

def colored_box(color, index):
    return rx.box(bg=color, width="1em", height="1em", border="1px solid white")

def index():
    return rx.vstack(
        rx.hstack(
            rx.button("PAUSE", on_click=State.turnOffTick, color_scheme="blue", border_radius="1em"),
            rx.button("RUN", on_click=State.turnOnTick, color_scheme="green", border_radius="1em"),
            rx.switch(is_checked=State.start, on_change=State.flip_switch),
        ),
        
        rx.hstack(
            rx.vstack(
                rx.heading("RATE", font_size="1em"),
                rx.heading(State.rate, font_size="2em"),
                bg_color="yellow",
                border_width="1px",
                padding_left="1em",
                padding_right="1em",

            ),
        
            rx.vstack(
                rx.heading("SCORE", font_size="1em"),
                rx.heading(State.score, font_size="2em"),
                bg_color="yellow",
                border_width="1px",
                padding_left="1em",
                padding_right="1em",

            ),
            rx.vstack(
                rx.heading("MAGIC", font_size="1em"),
                rx.heading(State.magic, font_size="2em"),
                bg_color="yellow",
                border_width="1px",
                padding_left="1em",
                padding_right="1em",
            ),
        ),
        # Usage of foreach, please refer https://reflex.app/docs/library/layout/foreach
        rx.responsive_grid(
            rx.foreach(
                State.cells,
                lambda color, idx: colored_box(color, idx),
            ),
            columns=[N],
        ),
        rx.hstack(
            rx.vstack(
                rx.button("￮", on_click=State.arrow_none, color_scheme="#FFFFFFFF", border_radius="1em",font_size="2em"),
                rx.button("￩", on_click=State.arrow_left, color_scheme="red", border_radius="1em",font_size="2em"),
            ),
            rx.vstack(
                rx.button("￪", on_click=State.arrow_up, color_scheme="red", border_radius="1em",font_size="2em"),
                rx.button("￬", on_click=State.arrow_down, color_scheme="red", border_radius="1em",font_size="2em"),
            ),
            rx.vstack(
                rx.button("￮", on_click=State.arrow_none, color_scheme="#FFFFFFFF", border_radius="1em",font_size="2em"),
                rx.button("￫", on_click=State.arrow_right, color_scheme="red", border_radius="1em",font_size="2em"),
            ),
        ),
        padding_top="3%",
    )

app = rx.App(state=State)
app.add_page(index, title="snake game")

app.compile()
