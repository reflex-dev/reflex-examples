from ..common import demo
from .json_tree import page

demo(
    route="/json_tree",
    title="JSON Tree (CSR, dynamic components)",
    description="Render nested JSON data as a tree using dynamic components from a state.",
)(page)