import uuid
from typing import Any, Dict
import reflex as rx


class Canvas(rx.Component):
    """https://docs.pmnd.rs/react-three-fiber/api/canvas"""

    tag = "Canvas"
    library = "@react-three/fiber"

    def get_event_triggers(self) -> Dict[str, Any]:
        return super().get_event_triggers() | {
            "on_pointer_missed": lambda: [],
        }


class ThreeCommon(rx.Component):
    args: rx.Var[Any]
    position: rx.Var[tuple[float, float, float]]
    rotation: rx.Var[tuple[float, float, float]]

    def _render(self) -> Dict[str, Any]:
        tag = super()._render()
        if tag.name:
            tag.name = tag.name[0].lower() + tag.name[1:]
        return tag


class EventData(rx.Base):
    intersections: list[Any]
    object: Any
    wheelDelta: int


def event_signature(event: EventData) -> list[Any]:
    return [event.object, event.intersections]


def wheel_event_signature(event: EventData) -> list[Any]:
    return [event.wheelDelta]


class mesh(ThreeCommon):
    tag = "Mesh"

    scale: rx.Var[float]

    def get_event_triggers(self) -> Dict[str, Any]:
        return super().get_event_triggers() | {
            "on_click": event_signature,
            "on_wheel": wheel_event_signature,
            "on_context_menu": event_signature,
            "on_pointer_over": event_signature,
            "on_pointer_out": event_signature,
            "on_pointer_missed": lambda: [],
        }


class boxGeometry(ThreeCommon):
    tag = "BoxGeometry"


class meshStandardMaterial(ThreeCommon):
    tag = "MeshStandardMaterial"

    color: rx.Var[str]


class ambientLight(ThreeCommon):
    tag = "AmbientLight"


class pointLight(ThreeCommon):
    tag = "PointLight"


class Edges(rx.Component):
    tag = "Edges"
    library = "@react-three/drei"


class State(rx.State):
    rotate_step: tuple[float, float, float] = (0.1, 0, 0)
    hovered: dict[str, bool] = {}
    active: str
    rotation: dict[str, tuple[float, float, float]] = {}

    @rx.cached_var
    def rotate_step_axis(self) -> str:
        max_step = max(self.rotate_step)
        if max_step == self.rotate_step[0]:
            return "x"
        if max_step == self.rotate_step[1]:
            return "y"
        return "z"

    def on_click(self, id):
        self.active = id

    def on_wheel(self, id, wheel_delta):
        self.active = id
        rotation = self.rotation.get(id, (0, 0, 0))
        step = 1 if wheel_delta > 0 else -1
        self.rotation[id] = (
            rotation[0] + step * self.rotate_step[0],
            rotation[1] + step * self.rotate_step[1],
            rotation[2] + step * self.rotate_step[2],
        )

    def on_pointer_missed(self):
        self.active = ""

    def on_pointer_over(self, id):
        self.hovered[id] = True

    def on_pointer_out(self, id):
        self.hovered[id] = False


def box(id, position):
    box_geometry = boxGeometry.create(args=[1, 1, 1])
    return mesh.create(
        box_geometry,
        meshStandardMaterial.create(
            color=rx.cond(State.hovered[id], "hotpink", "orange")
        ),
        Edges.create(),
        position=position,
        rotation=State.rotation[id],
        scale=rx.cond(State.active == id, 1.5, 1.0),
        on_click=lambda o, i: State.on_click(id),
        on_wheel=lambda wheel_delta: State.on_wheel(id, wheel_delta),
        on_pointer_over=lambda o, i: State.on_pointer_over(id),
        on_pointer_out=lambda o, i: State.on_pointer_out(id),
    )


def index() -> rx.Component:
    return rx.vstack(
        Canvas.create(
            ambientLight.create(),
            pointLight.create(position=(10, 10, 10)),
            box(str(uuid.uuid4()), (-1.2, 0, 0)),
            box(str(uuid.uuid4()), (1.2, 0, 0)),
            on_pointer_missed=State.on_pointer_missed,
        ),
        rx.hstack(
            rx.text("Rotation Axis:"),
            rx.radio_group(
                rx.radio("x", on_click=State.set_rotate_step((0.1, 0, 0))),
                rx.radio("y", on_click=State.set_rotate_step((0, 0.1, 0))),
                rx.radio("z", on_click=State.set_rotate_step((0, 0, 0.1))),
                value=State.rotate_step_axis,
            ),
        ),
    )


app = rx.App()
app.add_page(index)
app.compile()
