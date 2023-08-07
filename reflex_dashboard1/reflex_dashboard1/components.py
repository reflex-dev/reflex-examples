from reflex import Component
import reflex as rx


class Line(Component):
    tag = "Line"
    library = "react-chartjs-2"
    data: rx.Var[dict]
    options: rx.Var[dict] = {}
    plugins: rx.Var[list] = []
    redraw: rx.Var[bool] = False
    datasetIdKey: rx.Var[str] = "label"
    update_mode: rx.Var[str] = None

    def _get_imports(self):
        merged_imports = super()._get_imports()
        imp = {
            "chart.js": {
                rx.vars.ImportVar(tag="Chart"),
                rx.vars.ImportVar(tag="CategoryScale"),
                rx.vars.ImportVar(tag="LinearScale"),
                rx.vars.ImportVar(tag="PointElement"),
                rx.vars.ImportVar(tag="LineElement"),
                rx.vars.ImportVar(tag="Title"),
                rx.vars.ImportVar(tag="Tooltip"),
                rx.vars.ImportVar(tag="Legend"),
            }
        }
        return merged_imports | imp

    def _get_custom_code(self):
        return """
    Chart.register(CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    );
    """


line = Line.create
