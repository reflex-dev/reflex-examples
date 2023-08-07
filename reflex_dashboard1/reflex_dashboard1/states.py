import reflex as rx
class State(rx.State):
    """The app state."""

    display = True
    value: int = 3
    data: dict = {
        "labels": [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        "datasets": [
            {
                "label": "My Balance",
                "fill": False,
                "lineTension": 0.5,
                "backgroundColor": "#db86b2",
                "borderColor": "#B57295",
                "borderCapStyle": "butt",
                "borderDashOffset": 0.0,
                "borderJoinStyle": "#B57295",
                "pointBorderColor": "#B57295",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#B57295",
                "pointHoverBorderColor": "#B57295",
                "pointHoverBorderWidth": 2,
                "pointRadius": 1,
                "pointHitRadius": 10,
                "data": [
                    500,
                    300,
                    400,
                    500,
                    800,
                    650,
                    700,
                    690,
                    1000,
                    1200,
                    1050,
                    1300,
                ],
            },
        ],
    }

    def toggle(self):
        self.display = not self.display