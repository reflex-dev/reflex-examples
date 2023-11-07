"""The settings page for the template."""
from typing import Any
import asyncio
import httpx

import reflex as rx
from reflex.components.datadisplay.dataeditor import DataEditorTheme

from ..styles import *
from ..webui.state import State


class DataTableState(State):
    """Datatable state."""

    cols: list[Any] = [
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

    data = [
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
            "19 September, 1979",
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
            "6 December 1928",
            False,
            "Gryffindor",
            "16'  Oak unknown core",
            "None",
            "Part-Human (Half-giant)",
        ],
        [
            "6",
            "Fred Weasley",
            "1 April, 1978",
            True,
            "Gryffindor",
            "Unknown",
            "Unknown",
            "Pure-blood",
        ],
        [
            "7",
            "George Weasley",
            "1 April, 1978",
            True,
            "Gryffindor",
            "Unknown",
            "Unknown",
            "Pure-blood",
        ],
    ]


code_show = """rx.vstack(
    rx.box(
        rx.data_editor(
            columns=DataTableState.cols,
            data=DataTableState.data,
            draw_focus_ring=True,
            row_height=50,
            smooth_scroll_x=True,
            smooth_scroll_y=True,
            column_select="single",
            # style
            theme=DataEditorTheme(**darkTheme),
            width="80vw",
            height="80vh",
        ),
    ),
    rx.spacer(),
    height="100vh",
    spacing="25",
)"""

state_show = """class DataTableState(State):
    cols: list[Any] = [
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
    ]"""

data_show = """[
    ["1", "Harry James Potter", "31 July 1980", True, "Gryffindor", "11'  Holly  phoenix feather", "Stag", "Half-blood"],
    ["2", "Ronald Bilius Weasley", "1 March 1980", True,"Gryffindor", "12' Ash unicorn tail hair", "Jack Russell terrier", "Pure-blood"],
    ["3", "Hermione Jean Granger", "19 September, 1979", True, "Gryffindor", "10¾'  vine wood dragon heartstring", "Otter", "Muggle-born"],	
    ["4", "Albus Percival Wulfric Brian Dumbledore", "Late August 1881", True, "Gryffindor", "15' Elder Thestral tail hair core", "Phoenix", "Half-blood"],	
    ["5", "Rubeus Hagrid", "6 December 1928", False, "Gryffindor", "16'  Oak unknown core", "None", "Part-Human (Half-giant)"], 
    ["6", "Fred Weasley", "1 April, 1978", True, "Gryffindor", "Unknown", "Unknown", "Pure-blood"], 
    ["7", "George Weasley", "1 April, 1978", True, "Gryffindor", "Unknown", "Unknown", "Pure-blood"],
]"""


darkTheme = {
    "accent_color": "#8c96ff",
    "accent_light": "rgba(202, 206, 255, 0.253)",
    "text_dark": "#ffffff",
    "text_medium": "#b8b8b8",
    "text_light": "#a0a0a0",
    "text_bubble": "#ffffff",
    "bg_icon_header": "#b8b8b8",
    "fg_icon_header": "#000000",
    "text_header": "#a1a1a1",
    "text_header_selected": "#000000",
    "bg_cell": "#16161b",
    "bg_cell_medium": "#202027",
    "bg_header": "#212121",
    "bg_header_has_focus": "#474747",
    "bg_header_hovered": "#404040",
    "bg_bubble": "#212121",
    "bg_bubble_selected": "#000000",
    "bg_search_result": "#423c24",
    "border_color": "rgba(225,225,225,0.2)",
    "drilldown_border": "rgba(225,225,225,0.4)",
    "link_color": "#4F5DFF",
    "header_font_style": "bold 14px",
    "base_font_style": "13px",
    "font_family": "Inter, Roboto, -apple-system, BlinkMacSystemFont, avenir next, avenir, segoe ui, helvetica neue, helvetica, Ubuntu, noto, arial, sans-serif",
}

darkTheme_show = """darkTheme={
    "accent_color": "#8c96ff",
    "accent_light": "rgba(202, 206, 255, 0.253)",
    "text_dark": "#ffffff",
    "text_medium": "#b8b8b8",
    "text_light": "#a0a0a0",
    "text_bubble": "#ffffff",
    "bg_icon_header": "#b8b8b8",
    "fg_icon_header": "#000000",
    "text_header": "#a1a1a1",
    "text_header_selected": "#000000",
    "bg_cell": "#16161b",
    "bg_cell_medium": "#202027",
    "bg_header": "#212121",
    "bg_header_has_focus": "#474747",
    "bg_header_hovered": "#404040",
    "bg_bubble": "#212121",
    "bg_bubble_selected": "#000000",
    "bg_search_result": "#423c24",
    "border_color": "rgba(225,225,225,0.2)",
    "drilldown_border": "rgba(225,225,225,0.4)",
    "link_color": "#4F5DFF",
    "header_font_style": "bold 14px",
    "base_font_style": "13px",
    "font_family": "Inter, Roboto, -apple-system, BlinkMacSystemFont, avenir next, avenir, segoe ui, helvetica neue, helvetica, Ubuntu, noto, arial, sans-serif",
}"""


code_show_2 = """rx.vstack(
    rx.stack(
        rx.cond(
            ~DataTableLiveState.paused,
            rx.button("Pause", on_click=DataTableLiveState.toggle_pause),
            rx.button("Resume", on_click=DataTableLiveState.toggle_pause),
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
        theme=DataEditorTheme(**darkTheme),
        ),
    overflow_x="auto",
    width="100%",
    height="40vh",
)"""

data_show_2 = """We use the https://api.adviceslip.com API which produces example data like below:
        {'slip': {'id': 119, 'advice': "Don't assume anything is possible or impossible until you've asked the people who will be doing the work."}}
        {'slip': {'id': 190, 'advice': "Don't always believe what you think."}}
        {'slip': {'id': 1, 'advice': 'Remember that spiders are more afraid of you, than you are of them.'}}
        {'slip': {'id': 188, 'advice': 'Measure twice, cut once.'}}
        {'slip': {'id': 157, 'advice': 'When something goes wrong in life, just shout "plot twist!" and carry on.'}}
        {'slip': {'id': 39, 'advice': 'Never run a marathon in Crocs.'}}
        {'slip': {'id': 141, 'advice': "If you can't do anything about it, there's no point in worrying about it."}}
        {'slip': {'id': 198, 'advice': 'Sing in the shower.'}}
        {'slip': {'id': 218, 'advice': 'Gratitude is said to be the secret to happiness.'}}
        {'slip': {'id': 30, 'advice': 'When in doubt, just take the next small step.'}}
        {'slip': {'id': 91, 'advice': 'Drink a glass of water before meals.'}}
        {'slip': {'id': 95, 'advice': 'Good advice is something a man gives when he is too old to set a bad example.'}}
        {'slip': {'id': 198, 'advice': 'Sing in the shower.'}}"""

state_show_2 = """class DataTableLiveState(State):
    "The app state."

    paused: bool
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
            if self.paused:
                continue

            async with self:
                if len(self.table_data) > 50:
                    self.table_data.pop(0)

                res = httpx.get('https://api.adviceslip.com/advice')
                data = res.json()
                self.table_data.append({"v1": data["slip"]["id"], "v2": data["slip"]["advice"]})


    def toggle_pause(self):
        self.paused = not self.paused"""

class DataTableLiveState(State):
    """The app state."""

    # data: list[UpdateRow]
    paused: bool
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
                if self.paused:
                    continue
                
                if len(self.table_data) > 50:
                    self.table_data.pop(0)

                res = httpx.get('https://api.adviceslip.com/advice')
                data = res.json()
                self.table_data.append({"v1": data["slip"]["id"], "v2": data["slip"]["advice"]})


    def toggle_pause(self):
        self.paused = not self.paused



def pause_button():
    return rx.cond(
        ~DataTableLiveState.paused,
        rx.button("Pause", on_click=DataTableLiveState.toggle_pause),
        rx.button("Resume", on_click=DataTableLiveState.toggle_pause),
    )








def datatable_page() -> rx.Component:
    """The UI for the settings page.

    Returns:
        rx.Component: The UI for the settings page.
    """
    return rx.box(
        rx.vstack(
            rx.heading(
                "Data Table Demo",
                font_size="3em",
            ),
            rx.heading(
                "Simple Table Demo",
                font_size="2em",
            ),
            rx.box(
                rx.data_editor(
                    columns=DataTableState.cols,
                    data=DataTableState.data,
                    draw_focus_ring=True,
                    row_height=50,
                    smooth_scroll_x=True,
                    smooth_scroll_y=True,
                    column_select="single",
                    # style
                    theme=DataEditorTheme(**darkTheme),
                    ),
                    overflow_x="auto",
                    width="100%",
            ),
            rx.tabs(
                rx.tab_list(
                    rx.tab("Code", style=tab_style),
                    rx.tab("Data", style=tab_style),
                    rx.tab("State", style=tab_style),
                    rx.tab("Styling", style=tab_style),
                    padding_x=0,
                ),
                rx.tab_panels(
                    rx.tab_panel(
                        rx.code_block(
                            code_show,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            data_show,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            state_show,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            darkTheme_show,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    width="100%",
                ),
                variant="unstyled",
                color_scheme="purple",
                align="end",
                width="100%",
                padding_top=".5em",
            ),
            rx.heading(
                "Data Table Live Streaming Data Demo",
                font_size="2em",
            ),
            rx.vstack(
                rx.stack(
                    pause_button(),
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
                    theme=DataEditorTheme(**darkTheme),
                    ),
                overflow_x="auto",
                width="100%",
                height="35vh",
            ),
            rx.text("In this example we are live streaming data from an API and showcasing it within a ",
                rx.link(
                    "Table",
                    href="https://reflex.dev/docs/library/datadisplay/dataeditor/",
                    color="rgb(107,99,246)",
                ),
                ". We use ",
                rx.link(
                    "Background Events",
                    href="https://reflex.dev/docs/advanced-guide/background-tasks/",
                    color="rgb(107,99,246)",
                ),
                " to allow us to stream the data in the background and still interact with our UI."

            ),
            rx.tabs(
                rx.tab_list(
                    rx.tab("Code", style=tab_style),
                    rx.tab("Data", style=tab_style),
                    rx.tab("State", style=tab_style),
                    rx.tab("Styling", style=tab_style),
                    padding_x=0,
                ),
                rx.tab_panels(
                    rx.tab_panel(
                        rx.code_block(
                            code_show_2,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            data_show_2,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            state_show_2,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    rx.tab_panel(
                        rx.code_block(
                            darkTheme_show,
                            language="python",
                            theme="light",
                            show_line_numbers=True,
                        ),
                        width="100%",
                        padding_x=0,
                        padding_y=".25em",
                    ),
                    width="100%",
                ),
                variant="unstyled",
                color_scheme="purple",
                align="end",
                width="100%",
                padding_top=".5em",
            ),
            style=template_content_style,
        ),
        style=template_page_style,
    )
