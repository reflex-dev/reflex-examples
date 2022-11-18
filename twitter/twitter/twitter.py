"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
from .helpers import navbar, tweet
import datetime

class User(pc.Model, table=True):
    username: str
    password: str

class Tweet(pc.Model, table=True):
    username: str
    tweet: str
    time: str

class Friends(pc.Model, table=True):
    username: str
    friend: str
    
class State(pc.State):
    username: str
    password: str
    confirm_password: str

    logged_in: bool = False

    tweet: str
    show_tweet: bool = False
    tweets: list[Tweet] = []

    friend: str
    search: str
    def change(self):
        self.show_tweet = not (self.show_tweet)
        
    def post_tweet(self):
        if self.username == "":
            return pc.window_alert("Please log in to post a tweet.")
        with pc.session() as session:
            day= datetime.datetime.now()
            tweet = Tweet(username=self.username, tweet=self.tweet, time=day.strftime("%m/%d %H"))
            print("Tweeting")
            print(tweet)
            session.add(tweet)
            session.commit()
        self.show_tweet = not (self.show_tweet)

    def get_tweets(self):
        with pc.session() as session:
            print("Here")
            if self.search != "":
                self.tweets = session.query(Tweet).filter(Tweet.tweet.contains(self.search)).all()[::-1]
            else:
                self.tweets = session.query(Tweet).all()[::-1]
    
    def set_search(self, search):
        self.search = search
        with pc.session() as session:
            print("Here")
            if self.search != "":
                self.tweets = session.query(Tweet).filter(Tweet.tweet.contains(self.search)).all()[::-1]
            else:
                self.tweets = session.query(Tweet).all()[::-1]
    
    def login(self):
        with pc.session() as session:
            user = session.exec(User.select.where(User.username == self.username)).first()
            if (user and user.password == self.password):
                self.logged_in = True
                self.tweets = session.exec(Tweet.select).all()
                return pc.redirect("/home")
            else:
                return pc.window_alert("Invalid username or password.")
                  
    def logout(self):
        self.logged_in = False
        self.username = ""
        self.password = ""
        return pc.redirect("/")
    
    def signup(self):
        with pc.session() as session:
            if self.password != self.confirm_password:
                return pc.window_alert("Passwords do not match.")
            if session.exec(User.select.where(User.username == self.username)).first():
                return pc.window_alert("Username already exists.")
            user = User(username=self.username, password=self.password)
            session.add(user)
            session.commit()
            self.logged_in = True
            return pc.redirect("/home")
    
    def follow_user(self, user):
        with pc.session() as session:
            friend = Friends(username=self.username, friend=user)
            session.add(friend)
            session.commit()

    @pc.var
    def my_following(self) -> list[Friends]:
        if self.logged_in:
            with pc.session() as session:
                return session.exec(Friends.select.where(Friends.username == self.username)).all()
        else:
            return []

    @pc.var
    def my_followers(self) -> list[Friends]:
        if self.logged_in:
            with pc.session() as session:
                return session.exec(Friends.select.where(Friends.friend == self.username)).all()
        else:
            return []

    @pc.var
    def search_friends(self) -> list[Friends]:
        if self.logged_in and self.friend != "":
            with pc.session() as session:
                following = session.exec(Friends.select.where(Friends.username == self.username)).all()
                users = session.exec(User.select.where(User.username == self.friend, User.username != self.username)).all()
                return [user for user in users if user.username not in [friend.friend for friend in following]]
        return []
  
    
def home():
    return pc.center(
        navbar(State),
        pc.hstack(
            pc.vstack(
                pc.input(on_change=State.set_friend, placeholder="Add Friend", width="100%"),
                pc.foreach(
                    State.search_friends,
                    lambda friend: pc.vstack(
                            pc.hstack(
                                pc.avatar(name=friend.username, size="sm"),
                                pc.text(friend.username),
                                pc.spacer(),
                                pc.button(
                                    pc.icon(tag="AddIcon", color="white", height = "1em"), 
                                    on_click=lambda: State.follow_user(friend.username),
                                    bg = "rgb(29, 161, 242)"),
                                width = "100%"
                            ),

                            padding = "1em",
                            width = "100%"
                        ),
                ),
                pc.heading("Following", font_size =  "1.5em"),
                pc.divider(),
                pc.foreach(
                    State.my_following,
                    lambda friend: pc.vstack(
                            pc.hstack(
                                pc.avatar(name=friend.friend, size="sm"),
                                pc.text(friend.friend),
                            ),
                            padding = "1em",
                        ),
                ),
                pc.heading("Followers", font_size =  "1.5em"),
                pc.divider(),
                pc.foreach(
                    State.my_followers,
                    lambda friend: pc.vstack(
                            pc.hstack(
                                pc.avatar(name=friend.username, size="sm"),
                                pc.text(friend.username),
                            ),
                            padding = "1em",
                        ),
                ),
                pc.divider(),
                pc.center(
                    pc.button(
                    "Tweet",
                    on_click=State.change,
                    bg="rgb(29 161 242)",
                    color="white",
                    border_radius="full",
                    width = "100%"
                    ),
                    width = "100%"
                ),
                align_items="start",
                height="100vh",
                padding_x="1em",
                border_right="0.1em solid #F0F0F0",
                position="fixed",

            ),
            tweet(State),
            pc.vstack(
                pc.center(pc.icon(tag="ChevronUpIcon", on_click= State.get_tweets, height = "2em", width="2em")),
                pc.input(on_change=State.set_search, placeholder="Search", width="100%"),
                pc.foreach(
                    State.tweets,
                    lambda tweet: pc.vstack(
                            pc.hstack(
                                pc.avatar(name=tweet.username, size="sm"),
                                pc.text("@" + tweet.username),
                                pc.spacer(),
                                pc.text(tweet.time),
                                width = "100%",
                                align_items = "left",
                            ),
                            pc.divider(),
                            pc.text(tweet.tweet, width = "100%"),
                            padding = "1em",
                            border_color = "#ededed",
                            border_width = "1px",
                            border_radius = "lg",
                            shadow = "sm",
                            width = "100%",
                        ),
                ),
                align_items="top",
                padding_x = "5em",
                padding_left = "20em",
                max_height="80%",
                width = "100%",
            ),
            align_items="start",
            width = "100%",
            padding_x = "15%",
            overflow_y="scroll",
        ),
        padding_top = "6em",
    )

def login():
    return pc.center(
        pc.vstack(
            pc.input(on_blur=State.set_username, placeholder="Username", width="100%"),
            pc.input(on_blur=State.set_password, placeholder="Password", type_="password", width="100%"),
            pc.button("Login", on_click=State.login, width="100%"),
            pc.link(pc.button("Sign Up", width="100%"), href="/signup", width="100%"),
        ),
        shadow = "lg",
        padding = "1em",
        border_radius = "lg",
        background = "white",
    )

def signup():
    return pc.box(
        pc.vstack(
            pc.center(
                pc.vstack(
                    pc.heading("Sign Up", font_size =  "1.5em"),
                    pc.input(on_blur=State.set_username, placeholder="Username", width="100%"),
                    pc.input(on_blur=State.set_password, placeholder="Password", width="100%"),
                    pc.input(on_blur=State.set_confirm_password, placeholder="Confirm Password", width="100%"),
                    pc.button("Sign Up", on_click= State.signup, width="100%"),
                ),
                shadow = "lg",
                padding = "1em",
                border_radius = "lg",
                background = "white",
            )
        ),
        padding_top = "10em",
        text_align="top",
        position = "relative",
        width = "100%",
        height = "100vh",
        background_image = "signup.svg",
        background_size =  "100% auto"
    )

def index():
    return pc.box(
        pc.vstack(
            navbar(State),
            login(),
        ),
        padding_top = "10em",
        text_align="top",
        position = "relative",
        background_image = "bg.svg",
        background_size =  "100% auto",
        width = "100%",
        height = "100vh",
    )

app = pc.App(state=State)
app.add_page(index)
app.add_page(signup)
app.add_page(home)
app.compile()
