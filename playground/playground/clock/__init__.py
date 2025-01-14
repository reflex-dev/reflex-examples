from ..common import demo
from .clock import theme_ui

demo(
    route="/clock",
    title="Clock",
    description="A classic Reflex toy example, showing an analog and digital clock",
)(theme_ui)
