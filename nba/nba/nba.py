"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import reflex as rx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .helpers import navbar

nba_overview = "https://media.geeksforgeeks.org/wp-content/uploads/nba.csv"
nba_data = pd.read_csv(nba_overview)
college = sorted(nba_data["College"].unique().astype(str))


class State(rx.State):
    """The app state."""

    # Filters to apply to the data.
    position: str
    college: str
    age: tuple[int, int] = (0, 50)
    salary: tuple[int, int] = (0, 25000000)

    @rx.var
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

    @rx.var
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

    @rx.var
    def hist_fig(self) -> go.Figure:
        """The histogram figure."""
        nba = self.df

        if nba.empty:
            return go.Figure()
        else:
            return px.histogram(
                nba, x="Age", y="Salary", title="Age/Salary Distribution"
            )


def selection():
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.select(
                    ["C", "PF", "SF", "PG", "SG"],
                    placeholder="Select a position. (All)",
                    on_change=State.set_position,
                ),
                rx.select(
                    college,
                    placeholder="Select a college. (All)",
                    on_change=State.set_college,
                ),
            ),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.badge("Min Age: ", State.age[0]),
                        rx.spacer(),
                        rx.badge("Max Age: ", State.age[1]),
                    ),
                    rx.range_slider(on_change_end=State.set_age, min_=18, max_=50),
                    align_items="left",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.badge("Min Sal: ", State.salary[0] // 1000000, "M"),
                        rx.spacer(),
                        rx.badge("Max Sal: ", State.salary[1] // 1000000, "M"),
                    ),
                    rx.range_slider(
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
    return rx.center(
        rx.vstack(
            navbar(),
            selection(),
            rx.divider(),
            rx.plotly(data=State.scat_fig, layout={"width": "1000", "height": "600"}),
            rx.plotly(data=State.hist_fig, layout={"width": "1000", "height": "600"}),
            rx.data_table(
                data=nba_data,
                pagination=True,
                search=True,
                sort=True,
                resizable=True,
            ),
            rx.divider(),
            padding_top="6em",
            width="100%",
        )
    )


# Add state and page to the app.
app = rx.App(state=State)
app.add_page(index, title="NBA App")
