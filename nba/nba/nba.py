"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .helpers import navbar
from reflex.components.radix.themes import theme

nba_overview = "https://media.geeksforgeeks.org/wp-content/uploads/nba.csv"
nba_data = pd.read_csv(nba_overview)
college = ["All"] + sorted(nba_data["College"].unique().astype(str))


class State(rx.State):
    """The app state."""

    # Filters to apply to the data.
    position: str = "All"
    college: str = "All"
    age: tuple[int, int] = (18, 50)
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
                    ["All", "C", "PF", "SF", "PG", "SG"],
                    placeholder="Select a position.",
                    default="All",
                    on_change=State.set_position,
                    width="15em",
                    size="3",
                ),
                rx.select(
                    college,
                    placeholder="Select a college.",
                    default="All",
                    on_change=State.set_college,
                    width="15em",
                    size="3",
                ),
            ),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.badge("Min Age: ", State.age[0]),
                        rx.divider(orientation="vertical"),
                        rx.badge("Max Age: ", State.age[1]),
                    ),
                    rx.slider(
                        default_value=[18, 50],
                        min=18,
                        max=50,
                        on_value_commit=State.set_age,
                    ),
                    align_items="left",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.badge("Min Sal: ", State.salary[0] // 1000000, "M"),
                        rx.divider(orientation="vertical"),
                        rx.badge("Max Sal: ", State.salary[1] // 1000000, "M"),
                    ),
                    rx.slider(
                        default_value=[0, 25000000],
                        min=0,
                        max=25000000,
                        on_value_commit=State.set_salary,
                    ),
                    align_items="left",
                    width="100%",
                ),
            ),
            spacing="4",
        ),
        align="center",
        width="100%",
    )


def index():
    """The main view."""
    return rx.center(
        rx.vstack(
            navbar(),
            selection(),
            rx.divider(width="100%"),
            rx.plotly(data=State.scat_fig, layout={"width": "1000", "height": "600"}),
            rx.plotly(data=State.hist_fig, layout={"width": "1000", "height": "600"}),
            rx.data_table(
                data=nba_data,
                pagination=True,
                search=True,
                sort=True,
                resizable=True,
            ),
            rx.divider(width="100%"),
            align="center",
            padding_top="6em",
            width="100%",
        )
    )


app = rx.App(
    theme=theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="blue",
        gray_color="sand",
    )
)
app.add_page(index, title="NBA App")
