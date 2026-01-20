# Pressure Benchmark Data

This directory should contain structural data files from https://alexandria.icams.rub.de/data/pbe/benchmarks/pressure/

## Expected Data Format

The benchmark expects one of the following:

1. **Option A**: Individual structure files
   - Files named `{structure_name}.extxyz` containing atomic structures
   - Each file should be in extended XYZ format with cell information
   - Example: `example_structure.extxyz` (provided as reference)

2. **Option B**: A structures.json file with metadata
   ```json
   {
     "structure_name": {
       "file": "path/to/structure.extxyz",
       "reference_data": {
         "bulk_modulus": value_in_GPa,
         "volumes_at_pressure": {
           "0": volume_at_0_GPa,
           "10": volume_at_10_GPa,
           ...
         }
       }
     }
   }
   ```

## Downloading Data

To use this benchmark, download the pressure dataset from:
https://alexandria.icams.rub.de/data/pbe/benchmarks/pressure/

The data should be packaged as `pressure_structures.zip` containing the structure files.

Alternatively, place individual `.extxyz` structure files directly in this directory.

## Data Requirements

- Structure files should be in extended XYZ format (`.extxyz`)
- Each structure should contain:
  - Atomic positions
  - Cell parameters in the Lattice field
  - PBC (periodic boundary conditions) set to [True, True, True]
- Reference DFT calculations should have been performed using PBE functional

## Example Structure

See `example_structure.extxyz` for the expected format:
- FCC aluminum with lattice parameter 4.05 Å
- 2 atoms in the unit cell
- Lattice information in the header
- Periodic boundary conditions enabled

## Pressure Range

The benchmark tests structural relaxation at the following pressures:
- 0 GPa (ambient)
- 10 GPa
- 30 GPa
- 50 GPa
- 100 GPa
- 150 GPa

Results include:
- Relaxed volumes at each pressure
- Volume compression behavior
- Bulk modulus estimates from P-V curves
