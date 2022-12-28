"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .helpers import navbar

nba_overview = "https://media.geeksforgeeks.org/wp-content/uploads/nba.csv"
nba_data = pd.read_csv(nba_overview)
college = sorted(nba_data["College"].unique().astype(str))


class State(pc.State):
    """The app state."""

    position: str
    college: str
    age: list = [0, 50]
    salary: list = [0, 25000000]

    @pc.var
    def df(self) -> pd.DataFrame:
        """The data."""
        nba = nba_data[
            (nba_data["Age"] > int(self.age[0]))
            & (nba_data["Age"] < int(self.age[1]))
            & (nba_data["Salary"] > int(self.salary[0]))
            & (nba_data["Salary"] < int(self.salary[1]))
        ]

        if self.college and self.college != "All":
            nba = nba[nba["College"] == self.college]

        if self.position and self.position != "All":
            nba = nba[nba["Position"] == self.position]

        if nba.empty:
            return pd.DataFrame()
        else:
            return nba.fillna("")

    @pc.var
    def scat_fig(self) -> go.Figure:
        """The scatter figure."""
        nba = self.df

        if nba.empty:
            return go.Figure()
        else:
            return px.scatter(
                nba,
                x="Age",
                y="Salary",
                title="NBA Age/Salary plot",
                color=nba["Position"],
                hover_data=["Name"],
                symbol=nba["Position"],
                trendline="lowess",
                trendline_scope="overall",
            )

    @pc.var
    def hist_fig(self) -> go.Figure:
        """The histogram figure."""
        nba = self.df

        if nba.empty:
            return go.Figure()
        else:
            return px.histogram(
                nba, 
                x="Age", 
                y="Salary", 
                title="Age/Salary Distribution"
            )


def selection():
    return pc.vstack(
        pc.hstack(
            pc.vstack(
                pc.select(
                    ["C", "PF", "SF", "PG", "SG"],
                    placeholder="Select a position. (All)",
                    on_change=State.set_position,
                ),
                pc.select(
                    college,
                    placeholder="Select a college. (All)",
                    on_change=State.set_college,
                ),
            ),
            pc.vstack(
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min Age: ", State.age[0]),
                        pc.spacer(),
                        pc.badge("Max Age: ", State.age[1]),
                    ),
                    pc.range_slider(on_change_end=State.set_age, min_=18, max_=50),
                    align_items="left",
                    width="100%",
                ),
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min Sal: ", State.salary[0] // 1000000, "M"),
                        pc.spacer(),
                        pc.badge("Max Sal: ", State.salary[1] // 1000000, "M"),
                    ),
                    pc.range_slider(
                        on_change_end=State.set_salary, min_=0, max_=25000000
                    ),
                    align_items="left",
                    width="100%",
                ),
            ),
            spacing="1em",
        ),
        width="100%",
    )


def index():
    """The main view."""
    return pc.center(
        pc.vstack(
            navbar(),
            selection(),
            pc.divider(),
            pc.plotly(data=State.scat_fig, layout={"width": "1000", "height": "600"}),
            pc.plotly(data=State.hist_fig, layout={"width": "1000", "height": "600"}),
            pc.data_table(
                data=nba_data,
                pagination=True,
                search=True,
                sort=True,
                resizable=True,
            ),
            pc.divider(),
            padding_top="6em",
            width="100%",
        )
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="NBA App")
app.compile()
api = app.api
