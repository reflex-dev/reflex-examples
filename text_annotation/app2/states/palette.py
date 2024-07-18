from .base import Base

import uuid


class Palette(Base):

    selected_color: str

    def select_category_color(self, data: list[str]):

        if data[2] != "used":
            self.selected_color = data[0]

            self.palette = [
                (
                    [data[0], "solid", data[2]]
                    if color[0] == data[0]
                    else [
                        color[0],
                        "surface" if color[2] != "used" else "solid",
                        color[2],
                    ]
                )
                for color in self.palette
            ]

    def add_new_category(self):
        self.categories.append(
            {
                "id": str(uuid.uuid4()),
                "color": self.selected_color,
                "name": self.category_name,
                "type": "surface",
            }
        )

        self.palette = [
            (
                color
                if color[0] != self.selected_color
                else [self.selected_color, "solid", "used"]
            )
            for color in self.palette
        ]

    def select_category(self, data: dict[str, str]):
        data["type"] = "solid"

        self.categories = [
            (
                {
                    "id": item["id"],
                    "color": item["color"],
                    "name": item["name"],
                    "type": "surface",
                }
                if item["id"] != data["id"]
                else data
            )
            for item in self.categories
        ]

        self.selected_category = data["color"]
        self.current_label = data["name"]
