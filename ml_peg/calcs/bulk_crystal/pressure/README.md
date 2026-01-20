# Pressure Benchmark

This benchmark evaluates machine learning interatomic potentials (MLIPs) on their ability to predict structural properties of bulk crystals under external pressure ranging from 0 to 150 GPa.

## Overview

The pressure benchmark tests:
1. **Volume compression behavior**: How crystal volumes change with applied pressure
2. **Bulk modulus estimation**: Mechanical response to isotropic compression
3. **Structural stability**: Maintaining physically reasonable structures under extreme conditions

## Implementation Details

### Calculation (`calc_pressure.py`)

The benchmark performs the following steps:

1. **Data Loading**: Downloads structures from https://alexandria.icams.rub.de/data/pbe/benchmarks/pressure/ or uses locally available `.extxyz` files

2. **Pressure Points**: Tests at 0, 10, 30, 50, 100, and 150 GPa

3. **Relaxation Method**: 
   - Uses ASE's `StrainFilter` with `scalar_pressure` parameter
   - Allows cell relaxation while maintaining symmetry
   - BFGS optimizer with force convergence threshold of 0.05 eV/Å
   - Maximum 500 optimization steps

4. **Output**: For each structure and pressure:
   - Relaxed volume
   - Cell parameters
   - Atomic positions
   - Forces and stress tensor
   - Total energy

### Analysis (`analyse_pressure.py`)

Computes two primary metrics:

1. **Volume Compression**: Mean relative volume change from 0 to 150 GPa
   - Should show monotonic decrease with pressure
   - Typical compression: 5-20% at 150 GPa

2. **Bulk Modulus**: Estimated from P-V curve using B = -V(dP/dV)
   - Alternative to strain-based elastic constants
   - Tests mechanical response to compression

### Visualization (`app_pressure.py`)

Provides interactive plots:
- Volume vs. pressure scatter plots
- Parity plots comparing models
- Structure visualization at different pressures

## Running the Benchmark

### Prerequisites

```bash
pip install ml-peg
```

### Running Calculations

```bash
pytest --run-slow ml_peg/calcs/bulk_crystal/pressure/calc_pressure.py
```

Or for a specific model:

```bash
pytest --run-slow ml_peg/calcs/bulk_crystal/pressure/calc_pressure.py -k "model_name"
```

### Running Analysis

```bash
pytest ml_peg/analysis/bulk_crystal/pressure/analyse_pressure.py
```

### Viewing Results

```bash
python ml_peg/app/bulk_crystal/pressure/app_pressure.py
```

Then navigate to http://localhost:8055

## Data Format

### Input Structures

Place `.extxyz` files in `ml_peg/calcs/bulk_crystal/pressure/data/`

Expected format:
```
<number_of_atoms>
Lattice="<a_x> <a_y> <a_z> <b_x> <b_y> <b_z> <c_x> <c_y> <c_z>" Properties=species:S:1:pos:R:3 pbc="T T T"
<element> <x> <y> <z>
...
```

### Output Structure

Results are saved to:
```
ml_peg/calcs/bulk_crystal/pressure/outputs/
└── {model_name}/
    └── {structure_name}/
        ├── results.json           # Summary of all pressures
        ├── {structure}_P0GPa.extxyz
        ├── {structure}_P10GPa.extxyz
        └── ...
```

## Metrics

### Volume Compression
- **Unit**: Dimensionless (relative change)
- **Good**: < 0.05 (< 5% deviation)
- **Bad**: > 0.2 (> 20% deviation)
- **Level of Theory**: PBE

### Bulk Modulus
- **Unit**: GPa
- **Good**: < 10 GPa error
- **Bad**: > 50 GPa error
- **Level of Theory**: PBE

## Physical Context

Pressure-dependent properties are important for:
- Geophysics (Earth's interior, up to ~360 GPa at core)
- Materials synthesis (diamond anvil cells, up to ~400 GPa)
- Planetary science (giant planet interiors, up to TPa range)
- Shock physics and detonations

This benchmark focuses on the 0-150 GPa range, which covers:
- Lower mantle conditions (~24-136 GPa)
- Most laboratory high-pressure experiments
- Many materials synthesis conditions

## References

- Alexandria database: https://alexandria.icams.rub.de/
- ASE StrainFilter: https://wiki.fysik.dtu.dk/ase/ase/constraints.html
- Materials Project elasticity: https://docs.materialsproject.org/methodology/elasticity/

## Notes

- The benchmark uses ASE's `StrainFilter` which implements the Parrinello-Rahman method for constant pressure molecular dynamics
- Convergence can be slower at high pressures due to stiffer force constants
- Some structures may become unstable under extreme compression, indicated by negative cell volumes or non-convergence
- Reference data should be from PBE-level DFT calculations for consistency
