from ..common import demo
from .lorem_stream import example

demo(
    route="/lorem_stream",
    title="Lorem Streaming Background Tasks",
    description="Demonstrates how to use background tasks to stream text concurrently.",
)(example)
