"""Run calculations for pressure benchmark."""

from __future__ import annotations

from copy import copy
import json
from pathlib import Path
from typing import Any

from ase import Atoms
from ase.constraints import StrainFilter
from ase.io import read
from ase.optimize import BFGS
import pytest

from ml_peg.calcs.utils.utils import download_github_data
from ml_peg.models.get_models import load_models
from ml_peg.models.models import current_models

MODELS = load_models(current_models)

DATA_PATH = Path(__file__).parent / "data"
OUT_PATH = Path(__file__).parent / "outputs"

# Pressure values in GPa
PRESSURES = [0, 10, 30, 50, 100, 150]


def relax_under_pressure(
    atoms: Atoms,
    pressure_gpa: float,
    fmax: float = 0.05,
) -> Atoms:
    """
    Relax structure under constant external pressure.

    Parameters
    ----------
    atoms
        Atomic structure to relax.
    pressure_gpa
        External pressure in GPa.
    fmax
        Force convergence criterion in eV/Å.

    Returns
    -------
    Atoms
        Relaxed structure.
    """
    # Convert GPa to eV/Å³ (1 GPa = 0.00624150913 eV/Å³)
    pressure_ev_ang3 = pressure_gpa * 0.00624150913
    
    # Use StrainFilter to allow cell relaxation under pressure
    # scalar_pressure is the target external pressure
    sf = StrainFilter(atoms, scalar_pressure=pressure_ev_ang3)
    
    # Optimize structure
    opt = BFGS(sf, logfile=None)
    opt.run(fmax=fmax, steps=500)
    
    return atoms


@pytest.mark.slow
@pytest.mark.parametrize("mlip", MODELS.items())
def test_pressure(mlip: tuple[str, Any]) -> None:
    """
    Run pressure benchmark test.

    Parameters
    ----------
    mlip
        Name of model and model to get calculator.
    """
    model_name, model = mlip
    calc = model.get_calculator()

    # Try to download data from Alexandria repository
    # Note: The data should be available as a zip file at the specified URL
    try:
        data_dir = download_github_data(
            filename="pressure_structures.zip",
            github_uri="https://alexandria.icams.rub.de/data/pbe/benchmarks/pressure",
        )
    except Exception as e:
        # If download fails, check if data exists locally
        local_data_dir = DATA_PATH
        if list(local_data_dir.glob("*.extxyz")):
            data_dir = local_data_dir
        else:
            pytest.skip(
                f"Could not download pressure data from Alexandria repository: {e}. "
                "Please download the data manually and place it in the data/ directory."
            )

    # Load reference structures and metadata
    structures_path = data_dir / "structures.json"
    
    if not structures_path.exists():
        # If JSON doesn't exist, try loading structures from extxyz files in data directory
        structure_files = list(data_dir.glob("*.extxyz"))
        if not structure_files:
            pytest.skip(
                "No structure files found in pressure benchmark data. "
                "Please download data from https://alexandria.icams.rub.de/data/pbe/benchmarks/pressure/ "
                "and place it in ml_peg/calcs/bulk_crystal/pressure/data/"
            )
        structures_data = {}
        for struct_file in structure_files:
            name = struct_file.stem
            structures_data[name] = {"file": str(struct_file)}
    else:
        with open(structures_path) as file:
            structures_data = json.load(file)

    # Create output directory
    out_dir = OUT_PATH / model_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run calculations for each structure at different pressures
    for struct_name, struct_info in structures_data.items():
        # Load structure
        if "file" in struct_info:
            atoms = read(data_dir / struct_info["file"])
        else:
            # Build structure from data if file not provided
            atoms = read(data_dir / f"{struct_name}.extxyz")
        
        # Store reference data
        atoms.info["name"] = struct_name
        
        # Create structure-specific output directory
        struct_out_dir = out_dir / struct_name
        struct_out_dir.mkdir(parents=True, exist_ok=True)
        
        # Run relaxation at each pressure
        results = {}
        for pressure in PRESSURES:
            atoms_copy = atoms.copy()
            atoms_copy.calc = copy(calc)
            
            try:
                relaxed = relax_under_pressure(
                    atoms_copy,
                    pressure_gpa=pressure,
                    fmax=0.05,
                )
                
                # Store results
                results[f"pressure_{pressure}gpa"] = {
                    "volume": relaxed.get_volume(),
                    "cell": relaxed.cell.tolist(),
                    "positions": relaxed.positions.tolist(),
                    "forces": relaxed.get_forces().tolist(),
                    "stress": relaxed.get_stress().tolist(),
                    "energy": relaxed.get_potential_energy(),
                }
                
                # Write trajectory
                from ase.io import write
                write(
                    struct_out_dir / f"{struct_name}_P{pressure}GPa.extxyz",
                    relaxed,
                )
                
            except Exception as e:
                print(f"Failed to relax {struct_name} at {pressure} GPa: {e}")
                results[f"pressure_{pressure}gpa"] = {"error": str(e)}
        
        # Save results
        with open(struct_out_dir / "results.json", "w") as f:
            json.dump(results, f, indent=2)
