"""Run pressure benchmark app."""

from __future__ import annotations

from dash import Dash
from dash.html import Div

from ml_peg.app import APP_ROOT
from ml_peg.app.base_app import BaseApp
from ml_peg.app.utils.build_callbacks import plot_from_table_column
from ml_peg.app.utils.load import read_plot
from ml_peg.models.get_models import get_model_names
from ml_peg.models.models import current_models

MODELS = get_model_names(current_models)
BENCHMARK_NAME = "Pressure"
DOCS_URL = "https://ddmms.github.io/ml-peg/user_guide/benchmarks/bulk_crystal.html#pressure"
DATA_PATH = APP_ROOT / "data" / "bulk_crystal" / "pressure"


class PressureApp(BaseApp):
    """Pressure benchmark app layout and callbacks."""

    def register_callbacks(self) -> None:
        """Register callbacks to app."""
        volumes_plot = read_plot(
            DATA_PATH / "figure_volumes_vs_pressure.json", id=f"{BENCHMARK_NAME}-figure"
        )

        plot_from_table_column(
            table_id=self.table_id,
            plot_id=f"{BENCHMARK_NAME}-figure-placeholder",
            column_to_plot={
                "Volume Compression": volumes_plot,
            },
        )


def get_app() -> PressureApp:
    """
    Get pressure benchmark app layout and callback registration.

    Returns
    -------
    PressureApp
        Benchmark layout and callback registration.
    """
    return PressureApp(
        name=BENCHMARK_NAME,
        description=(
            "Performance when predicting structural properties of bulk crystals "
            "under external pressure (0-150 GPa). Tests the ability to accurately "
            "model compression behavior and bulk moduli."
        ),
        docs_url=DOCS_URL,
        table_path=DATA_PATH / "pressure_metrics_table.json",
        extra_components=[
            Div(id=f"{BENCHMARK_NAME}-figure-placeholder"),
        ],
    )


if __name__ == "__main__":
    full_app = Dash(__name__, assets_folder=DATA_PATH.parent.parent)
    pressure_app = get_app()
    full_app.layout = pressure_app.layout
    pressure_app.register_callbacks()
    full_app.run(port=8055, debug=True)
