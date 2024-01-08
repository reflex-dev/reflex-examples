import reflex as rx
from typing import Any
import asyncio
import httpx


class BaseState(rx.State):
    pass


class DataTableState(BaseState):
    """The app state."""

    clicked_cell: str = "Cell clicked: "
    edited_cell: str = "Cell edited: "
    right_clicked_group_header: str = "Group header right clicked: "
    item_hovered: str = "Item Hovered: "
    deleted: str = "Deleted: "

    cols: list[dict] = [
        {"title": "Title", "type": "str"},
        {
            "title": "Name",
            "type": "str",
            "group": "Data",
            "width": 300,
        },
        {
            "title": "Birth",
            "type": "str",
            "group": "Data",
            "width": 150,
        },
        {
            "title": "Human",
            "type": "bool",
            "group": "Data",
            "width": 80,
        },
        {
            "title": "House",
            "type": "str",
            "group": "Data",
        },
        {
            "title": "Wand",
            "type": "str",
            "group": "Data",
            "width": 250,
        },
        {
            "title": "Patronus",
            "type": "str",
            "group": "Data",
        },
        {
            "title": "Blood status",
            "type": "str",
            "group": "Data",
            "width": 200,
        },
    ]

    data: list[str] = [
        [
            "1",
            "Harry James Potter",
            "31 July 1980",
            True,
            "Gryffindor",
            "11'  Holly  phoenix feather",
            "Stag",
            "Half-blood",
        ],
        [
            "2",
            "Ronald Bilius Weasley",
            "1 March 1980",
            True,
            "Gryffindor",
            "12' Ash unicorn tail hair",
            "Jack Russell terrier",
            "Pure-blood",
        ],
        [
            "3",
            "Hermione Jean Granger",
            "19 September, 1979",
            True,
            "Gryffindor",
            "10¾'  vine wood dragon heartstring",
            "Otter",
            "Muggle-born",
        ],
        [
            "4",
            "Albus Percival Wulfric Brian Dumbledore",
            "Late August 1881",
            True,
            "Gryffindor",
            "15' Elder Thestral tail hair core",
            "Phoenix",
            "Half-blood",
        ],
        [
            "5",
            "Rubeus Hagrid",
            "6 December 1928",
            False,
            "Gryffindor",
            "16'  Oak unknown core",
            "None",
            "Part-Human (Half-giant)",
        ],
        [
            "6",
            "Fred Weasley",
            "1 April, 1978",
            True,
            "Gryffindor",
            "Unknown",
            "Unknown",
            "Pure-blood",
        ],
        [
            "7",
            "George Weasley",
            "1 April, 1978",
            True,
            "Gryffindor",
            "Unknown",
            "Unknown",
            "Pure-blood",
        ],
    ]

    def get_clicked_data(self, pos) -> str:
        self.clicked_cell = f"Cell clicked: {pos}"

    def get_edited_data(self, pos, val) -> str:
        col, row = pos
        self.data[row][col] = val["data"]
        self.edited_cell = f"Cell edited: {pos}, Cell value: {val['data']}"

    def get_group_header_right_click(self, index, val):
        self.right_clicked_group_header = f"Group header right clicked at index: {index}, Group header value: {val['group']}"

    def get_item_hovered(self, pos) -> str:
        self.item_hovered = (
            f"Item Hovered type: {pos['kind']}, Location: {pos['location']}"
        )

    def get_deleted_item(self, selection):
        self.deleted = f"Deleted cell: {selection['current']['cell']}"

    # def append_row(self):
    #     print("13232")

    def column_resize(self, col, width):
        self.cols[col["pos"]]["width"] = width


class DataTableLiveState(BaseState):
    "The app state."

    running: bool
    table_data: list[dict[str, Any]] = []
    rate: int = 0.4
    columns: list[dict[str, str]] = [
        {
            "title": "id",
            "id": "v1",
            "type": "int",
            "width": 100,
        },
        {
            "title": "advice",
            "id": "v2",
            "type": "str",
            "width": 750,
        },
    ]

    @rx.background
    async def live_stream(self):
        while True:
            await asyncio.sleep(1 / self.rate)
            async with self:
                if not self.running:
                    break

                if len(self.table_data) > 50:
                    self.table_data.pop(0)

                res = httpx.get("https://api.adviceslip.com/advice")
                data = res.json()
                self.table_data.append(
                    {"v1": data["slip"]["id"], "v2": data["slip"]["advice"]}
                )

    def toggle_pause(self):
        self.running = not self.running
        if self.running:
            return DataTableLiveState.live_stream


darkTheme = {
    "accentColor": "#8c96ff",
    "accentLight": "rgba(202, 206, 255, 0.253)",
    "textDark": "#ffffff",
    "textMedium": "#b8b8b8",
    "textLight": "#a0a0a0",
    "textBubble": "#ffffff",
    "bgIconHeader": "#b8b8b8",
    "fgIconHeader": "#000000",
    "textHeader": "#a1a1a1",
    "textHeaderSelected": "#000000",
    "bgCell": "#16161b",
    "bgCellMedium": "#202027",
    "bgHeader": "#212121",
    "bgHeaderHasFocus": "#474747",
    "bgHeaderHovered": "#404040",
    "bgBubble": "#212121",
    "bgBubbleSelected": "#000000",
    "bgSearchResult": "#423c24",
    "borderColor": "rgba(225,225,225,0.2)",
    "drilldownBorder": "rgba(225,225,225,0.4)",
    "linkColor": "#4F5DFF",
    "headerFontStyle": "bold 14px",
    "baseFontStyle": "13px",
    "fontFamily": "Inter, Roboto, -apple-system, BlinkMacSystemFont, avenir next, avenir, segoe ui, helvetica neue, helvetica, Ubuntu, noto, arial, sans-serif",
}


tab_style = {
    "color": "#494369",
    "font_weight": 600,
    "_selected": {
        "color": "#5646ED",
        "bg": "#F5EFFE",
        "padding_x": "0.5em",
        "padding_y": "0.25em",
        "border_radius": "8px",
    },
}


def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.vstack(
            rx.heading("Data Table Demo!", font_size="2em"),
            rx.vstack(
                rx.tabs(
                    rx.tab_list(
                        rx.tab("Static Data", style=tab_style),
                        rx.tab("Live Data", style=tab_style),
                    ),
                    rx.tab_panels(
                        rx.tab_panel(
                            rx.vstack(
                                rx.heading(
                                    DataTableState.clicked_cell, size="lg", color="blue"
                                ),
                                rx.heading(
                                    DataTableState.edited_cell, size="lg", color="green"
                                ),
                                rx.heading(
                                    DataTableState.right_clicked_group_header,
                                    size="lg",
                                    color="orange",
                                ),
                                rx.heading(
                                    DataTableState.item_hovered,
                                    size="lg",
                                    color="purple",
                                ),
                                rx.heading(
                                    DataTableState.deleted, size="lg", color="red"
                                ),
                                rx.data_editor(
                                    columns=DataTableState.cols,
                                    data=DataTableState.data,
                                    # rows=10,
                                    on_paste=True,
                                    draw_focus_ring=False,
                                    # fixed_shadow_x=True,
                                    freeze_columns=2,
                                    group_header_height=100,
                                    header_height=80,
                                    # max_column_auto_width=200,
                                    # this works just need to describe it
                                    # max_column_width=200,
                                    min_column_width=100,
                                    row_height=50,
                                    row_markers="clickable-number",
                                    # also mention smooth_scroll_y
                                    smooth_scroll_x=True,
                                    vertical_border=False,
                                    column_select="multi",
                                    # prevent_diagonal_scrolling=False,
                                    overscroll_x=0,
                                    on_cell_clicked=DataTableState.get_clicked_data,
                                    on_cell_edited=DataTableState.get_edited_data,
                                    on_group_header_context_menu=DataTableState.get_group_header_right_click,
                                    on_item_hovered=DataTableState.get_item_hovered,
                                    on_delete=DataTableState.get_deleted_item,
                                    # on_row_appended=DataTableState.append_row,
                                    on_column_resize=DataTableState.column_resize,
                                    theme=darkTheme,
                                    width="80vw",
                                    height="80vh",
                                ),
                            ),
                        ),
                        rx.tab_panel(
                            rx.vstack(
                                rx.stack(
                                    rx.cond(
                                        ~DataTableLiveState.running,
                                        rx.button(
                                            "Start",
                                            on_click=DataTableLiveState.toggle_pause,
                                            color_scheme="green",
                                        ),
                                        rx.button(
                                            "Pause",
                                            on_click=DataTableLiveState.toggle_pause,
                                            color_scheme="red",
                                        ),
                                    ),
                                ),
                                rx.data_editor(
                                    columns=DataTableLiveState.columns,
                                    data=DataTableLiveState.table_data,
                                    draw_focus_ring=True,
                                    row_height=50,
                                    smooth_scroll_x=True,
                                    smooth_scroll_y=True,
                                    column_select="single",
                                    # style
                                    theme=darkTheme,
                                ),
                                overflow_x="auto",
                                width="100%",
                            ),
                        ),
                    ),
                    spacing="1.5em",
                    font_size="2em",
                    padding_top="10vh",
                    width="90vw",
                ),
            ),
        ),
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index)
