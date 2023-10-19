import asyncio
from datetime import datetime
from typing import Any, Literal

import reflex as rx

from reflex.utils import format

# from pandas import DataFrame


# df = DataFrame({"A": [1, 2], "B": ["foo", "bar"]})


class ToastProvider(rx.components.libs.chakra.ChakraComponent):
    tag = "useToast"

    def _get_hooks(self) -> str | None:
        return "refs['__toast'] = useToast()"

    @staticmethod
    def show(
        title: str,
        description: str,
        duration: int,
        status: Literal["info", "warning", "success", "error", "loading"] = "info",
    ) -> rx.event.EventSpec:
        return rx.call_script(
            f"""
            refs['__toast']({{
            title: "{title}",
            description: "{description}",
            duration: {duration},
            status: "{status}",
            isClosable: true,
            }})
        """
        )


TP = ToastProvider


class State(rx.State):
    cols1: list[Any] = [
        "Title",
        {"title": "Select", "type": "bool"},
    ]
    cols2: list[Any] = [
        {"title": "Title", "type": "str"},
        {
            "title": "Bool",
            "type": "bool",
            "group": "Data",
        },
        {
            "title": "Date",
            "type": "datetime",
            "id": "date",
            "group": "Data",
        },
        {
            "title": "Foo",
            "type": "int",
            "id": "date",
            "readOnly": True,
            "group": "Data",
        },
        {
            "title": "Bar",
            "type": "str",
            "id": "date",
            "group": "Data",
        },
    ]
    data = [
        ["1", True, datetime.now(), 0, "A", "A", "A"],
        ["2", False, datetime.now(), 0, "A", "A", "A"],
        ["3", True, datetime.now(), 0, "A", "A", "A"],
        ["4", False, datetime.now(), 0, "A", "A", "A"],
        ["5", False, datetime.now(), 0, "A", "A", "A"],
        ["6", False, datetime.now(), 0, "A", "A", "A"],
        ["7", False, datetime.now(), 0, "A", "A", "A"],
        ["8", False, datetime.now(), 0, "A", "A", "A"],
        ["9", False, datetime.now(), 0, "A", "A", "A"],
        ["10", False, datetime.now(), 0, "A", "A", "A"],
    ]
    # df: DataFrame = df

    @rx.var
    def c_cols1(self) -> list[dict[str, Any]]:
        return [format.format_data_editor_column(c) for c in self.cols1]

    def edit_cell(self, pos, value):
        col, row = pos
        self.data[row][col] = value["data"]
        yield CtrlState.send_alert("Cell edited", pos, value["data"])

    @rx.var
    def selected(self) -> list:
        return [",".join([row[0] for row in self.data if row[1]])]


class CtrlState(State):
    draw_focus_ring = True
    fixed_shadow_x = False
    fixed_shadow_y = False
    smooth_scroll_x = False
    smooth_scroll_y = False
    vertical_border = False
    freeze_columns = 0
    row_height: int = 20
    row_marker: str = "both"
    row_marker_width = 15
    group_header_height = 20
    header_height = 20
    max_column_auto_width = 100
    min_column_width = 100
    max_column_width = 300
    row_marker_start_index = 0
    column_select = "single"

    def send_alert(self, msg, data=None, data2=None):
        if data2:
            yield TP.show(
                title="DataTable Demo",
                description=f"{msg} {data} {data2}",
                status="info",
                duration=2000,
            )
        elif data:
            yield TP.show(
                title="DataTable Demo",
                description=f"{msg} {data}",
                status="info",
                duration=2000,
            )
        else:
            yield TP.show(
                title="DataTable Demo",
                description=f"{msg}",
                status="info",
                duration=2000,
            )


def get_dyn_setter(var: rx.Var):
    return CtrlState.event_handlers[var.get_setter_name().rpartition(".")[-1]]


def controller_item(var, ctrl):
    return rx.hstack(rx.text(var._var_name, ": "), ctrl, rx.text(var), width="100%")


def controller_line(_list):
    return rx.hstack(
        *[controller_checkbox(v) for v in _list],
        width="100%",
    )


def controller_checkbox(var):
    return controller_item(
        var, rx.checkbox(is_checked=var, on_change=get_dyn_setter(var))
    )


def controller_slider(var, min_, max_):
    return controller_item(
        var, rx.slider(value=var, on_change=get_dyn_setter(var), min_=min_, max_=max_)
    )


def controller_select(var, options):
    return controller_item(
        var, rx.select(options, value=var, on_change=get_dyn_setter(var))
    )


def controller():
    return rx.vstack(
        rx.hstack(rx.heading("Parameters"), rx.color_mode_switch()),
        rx.divider(border_color="black", width="100%"),
        controller_line(
            [
                CtrlState.draw_focus_ring,
                CtrlState.fixed_shadow_x,
                CtrlState.fixed_shadow_y,
            ]
        ),
        controller_line(
            [
                CtrlState.vertical_border,
                CtrlState.smooth_scroll_x,
                CtrlState.smooth_scroll_y,
            ]
        ),
        controller_slider(CtrlState.freeze_columns, 0, 5),
        controller_slider(CtrlState.group_header_height, 20, 50),
        controller_slider(CtrlState.header_height, 20, 50),
        controller_slider(CtrlState.max_column_auto_width, 200, 300),
        controller_slider(CtrlState.max_column_width, 300, 500),
        controller_slider(CtrlState.min_column_width, 100, 300),
        controller_slider(CtrlState.row_height, 20, 100),
        controller_select(
            CtrlState.row_marker,
            ["number", "none", "checkbox", "both", "clickable-number"],
        ),
        controller_slider(CtrlState.row_marker_start_index, -5, 5),
        controller_slider(CtrlState.row_marker_width, 20, 50),
        controller_select(CtrlState.column_select, ["none", "single", "multi"]),
        rx.spacer(),
        height="100vh",
        width="30vw",
    )


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


@rx.page(route="/")
def idx():
    return rx.hstack(
        controller(),
        rx.divider(orientation="vertical", height="100vh", border="solid black 1px"),
        rx.vstack(
            TP.create(),
            rx.data_editor(
                rows=10,
                columns=State.cols2,
                data=State.data,
                draw_focus_ring=CtrlState.draw_focus_ring,
                fixed_shadow_x=CtrlState.fixed_shadow_x,
                fixed_shadow_y=CtrlState.fixed_shadow_y,
                freeze_columns=CtrlState.freeze_columns,
                group_header_height=CtrlState.group_header_height,
                header_height=CtrlState.header_height,
                max_column_auto_width=CtrlState.max_column_auto_width,
                max_column_width=CtrlState.max_column_width,
                min_column_width=CtrlState.min_column_width,
                row_height=CtrlState.row_height,
                row_markers=CtrlState.row_marker,
                row_marker_width=CtrlState.row_marker_width,
                row_marker_start_index=CtrlState.row_marker_start_index,
                smooth_scroll_x=CtrlState.smooth_scroll_x,
                smooth_scroll_y=CtrlState.smooth_scroll_y,
                vertical_border=CtrlState.vertical_border,
                column_select=CtrlState.column_select,
                # style
                theme=darkTheme,
                # event handlers
                on_cell_edited=CtrlState.edit_cell,
                on_cell_activated=lambda pos: CtrlState.send_alert(
                    "on_cell_activated: ", pos
                ),
                on_cell_clicked=lambda pos: CtrlState.send_alert(
                    "on_cell_clicked: ", pos
                ),
                on_cell_context_menu=lambda pos: CtrlState.send_alert(
                    "on_cell_context_menu: ", pos
                ),
                on_group_header_clicked=lambda idx, data: CtrlState.send_alert(
                    "on_group_header_clicked: ", idx, data
                ),
                on_group_header_context_menu=lambda idx, data: CtrlState.send_alert(
                    "on_group_header_context_menu: ", idx, data
                ),
                on_header_clicked=lambda pos: CtrlState.send_alert(
                    "on_header_clicked: ", pos
                ),
                on_header_context_menu=lambda pos: CtrlState.send_alert(
                    "on_header_context_menu: ", pos
                ),
                on_header_menu_click=lambda col, pos: CtrlState.send_alert(
                    "on_header_menu_click: ", col, pos
                ),
                height="30vh",
                # onItemHovered=lambda pos: CtrlState.send_alert("", pos),
                # onDelete=lambda selection: CtrlState.send_alert("onDelete", selection),
                # onSelectionCleared=CtrlState.send_alert("onSelectionCleared"),
            ),
            rx.spacer(),
            height="100vh",
            spacing="25",
        ),
    )


app = rx.App()
app.compile()
