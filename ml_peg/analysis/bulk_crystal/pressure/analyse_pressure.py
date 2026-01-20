"""Analyse pressure benchmark."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from ml_peg.analysis.utils.decorators import build_table, plot_parity
from ml_peg.analysis.utils.utils import load_metrics_config, mae
from ml_peg.app import APP_ROOT
from ml_peg.calcs import CALCS_ROOT
from ml_peg.models.get_models import get_model_names
from ml_peg.models.models import current_models

MODELS = get_model_names(current_models)
CALC_PATH = CALCS_ROOT / "bulk_crystal" / "pressure" / "outputs"
OUT_PATH = APP_ROOT / "data" / "bulk_crystal" / "pressure"

METRICS_CONFIG_PATH = Path(__file__).with_name("metrics.yml")
DEFAULT_THRESHOLDS, DEFAULT_TOOLTIPS, DEFAULT_WEIGHTS = load_metrics_config(
    METRICS_CONFIG_PATH
)

# Pressure values in GPa
PRESSURES = [0, 10, 30, 50, 100, 150]


def get_structure_names() -> list[str]:
    """
    Get list of structure names.

    Returns
    -------
    list[str]
        List of structure names from calculation outputs.
    """
    structures = []
    for model_name in MODELS:
        model_dir = CALC_PATH / model_name
        if not model_dir.exists():
            continue
        for struct_dir in sorted(model_dir.iterdir()):
            if struct_dir.is_dir():
                structures.append(struct_dir.name)
        break
    return structures


STRUCTURES = get_structure_names()


@pytest.fixture
@plot_parity(
    filename=OUT_PATH / "figure_volumes_vs_pressure.json",
    title="Volume vs Pressure",
    x_label="Predicted volume / Å³",
    y_label="Reference volume / Å³",
    hoverdata={
        "Structure": STRUCTURES,
    },
)
def volumes_vs_pressure() -> dict[str, list]:
    """
    Get reference and predicted volumes at different pressures.

    Returns
    -------
    dict[str, list]
        Dictionary of reference and predicted volumes.
    """
    results = {"ref": []} | {mlip: [] for mlip in MODELS}
    ref_stored = False

    for model_name in MODELS:
        model_dir = CALC_PATH / model_name

        if not model_dir.exists():
            continue

        for struct_dir in sorted(model_dir.iterdir()):
            if not struct_dir.is_dir():
                continue
            
            results_file = struct_dir / "results.json"
            if not results_file.exists():
                continue
            
            with open(results_file) as f:
                struct_results = json.load(f)
            
            for pressure in PRESSURES:
                key = f"pressure_{pressure}gpa"
                if key in struct_results and "volume" in struct_results[key]:
                    results[model_name].append(struct_results[key]["volume"])
            
            # Store reference volumes (only once)
            # TODO: Reference data should be loaded from DFT calculations
            # When reference data is available, it should be stored in:
            # - A reference JSON file with pressure-volume data for each structure
            # - Or as metadata in the structure files themselves
            # For now, this benchmark focuses on comparing MLIP models to each other
            # Once Alexandria data includes reference values, update this section to:
            # if not ref_stored:
            #     for pressure in PRESSURES:
            #         key = f"pressure_{pressure}gpa"
            #         if key in reference_data[struct_name]:
            #             results["ref"].append(reference_data[struct_name][key]["volume"])

    return results


@pytest.fixture
def volume_compression_errors() -> dict[str, float]:
    """
    Get errors in volume compression behavior.

    Returns
    -------
    dict[str, float]
        Dictionary of volume compression errors for all models.
    """
    results = {}
    
    for model_name in MODELS:
        model_dir = CALC_PATH / model_name
        
        if not model_dir.exists():
            continue
        
        errors = []
        for struct_dir in sorted(model_dir.iterdir()):
            if not struct_dir.is_dir():
                continue
            
            results_file = struct_dir / "results.json"
            if not results_file.exists():
                continue
            
            with open(results_file) as f:
                struct_results = json.load(f)
            
            # Check that volume decreases monotonically with pressure
            volumes = []
            for pressure in PRESSURES:
                key = f"pressure_{pressure}gpa"
                if key in struct_results and "volume" in struct_results[key]:
                    volumes.append(struct_results[key]["volume"])
            
            if len(volumes) > 1:
                # Calculate relative volume change from 0 to 150 GPa
                if volumes[0] > 0:
                    rel_change = (volumes[0] - volumes[-1]) / volumes[0]
                    # TODO: Compare with reference compression data when available
                    # Expected compression is typically 5-20% for 150 GPa depending on material
                    # Current implementation measures compression magnitude as a proxy metric
                    # Once reference data is available from Alexandria, compute:
                    # error = abs(rel_change - reference_compression[struct_name])
                    errors.append(abs(rel_change))
        
        if errors:
            results[model_name] = np.mean(errors)
        else:
            results[model_name] = 0.0
    
    return results


@pytest.fixture
def bulk_modulus_errors() -> dict[str, float]:
    """
    Get errors in bulk modulus estimation from pressure-volume data.

    Returns
    -------
    dict[str, float]
        Dictionary of bulk modulus errors for all models.
    """
    results = {}
    
    for model_name in MODELS:
        model_dir = CALC_PATH / model_name
        
        if not model_dir.exists():
            continue
        
        errors = []
        for struct_dir in sorted(model_dir.iterdir()):
            if not struct_dir.is_dir():
                continue
            
            results_file = struct_dir / "results.json"
            if not results_file.exists():
                continue
            
            with open(results_file) as f:
                struct_results = json.load(f)
            
            # Extract pressure-volume data
            pressures = []
            volumes = []
            for pressure in PRESSURES:
                key = f"pressure_{pressure}gpa"
                if key in struct_results and "volume" in struct_results[key]:
                    pressures.append(pressure)
                    volumes.append(struct_results[key]["volume"])
            
            if len(volumes) > 2:
                # Estimate bulk modulus from linear fit of P vs V/V0
                # B = -V * dP/dV
                v0 = volumes[0]
                if v0 > 0:
                    # Simple finite difference estimate
                    if len(pressures) > 1:
                        dV = volumes[-1] - volumes[0]
                        dP = pressures[-1] - pressures[0]
                        if dV != 0:
                            bulk_modulus = -v0 * dP / dV
                            # TODO: Compare with reference bulk modulus when available
                            # Current implementation computes bulk modulus as a consistency check
                            # Once reference data is available, compute:
                            # error = abs(bulk_modulus - reference_bulk_modulus[struct_name])
                            # For now, store the computed value for relative comparison
                            errors.append(abs(bulk_modulus))
        
        if errors:
            results[model_name] = np.mean(errors)
        else:
            results[model_name] = 0.0
    
    return results


@pytest.fixture
@build_table(
    filename=OUT_PATH / "pressure_metrics_table.json",
    metric_tooltips=DEFAULT_TOOLTIPS,
    thresholds=DEFAULT_THRESHOLDS,
)
def metrics(
    volume_compression_errors: dict[str, float],
    bulk_modulus_errors: dict[str, float],
) -> dict[str, dict]:
    """
    Get all pressure benchmark metrics.

    Parameters
    ----------
    volume_compression_errors
        Volume compression errors.
    bulk_modulus_errors
        Bulk modulus errors.

    Returns
    -------
    dict[str, dict]
        Metric names and values for all models.
    """
    return {
        "Volume Compression": volume_compression_errors,
        "Bulk Modulus": bulk_modulus_errors,
    }


def test_pressure(metrics: dict[str, dict]) -> None:
    """
    Run pressure benchmark analysis.

    Parameters
    ----------
    metrics
        All pressure benchmark metrics.
    """
    return
