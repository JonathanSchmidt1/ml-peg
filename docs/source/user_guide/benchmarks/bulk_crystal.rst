=============
Bulk Crystals
=============

Lattice constants
=================

Summary
-------

Performance in evaluating lattice constants for 23 solids, including pure elements,
binary compounds, and semiconductors.


Metrics
-------

1. MAE (Experimental)

Mean lattice constant error compared to experimental data

For each formula, a bulk crystal is built using the experimental lattice constants and
lattice type for the initial structure. This structure is optimised for each model
using the LBFGS optimiser, with the FrechetCellFilter applied to allow optimisation of
the cell, until the largest absolute Cartesian component of any interatomic force is
less than 0.03 eV/Å. The lattice constants of this optimised structure are then
compared to experimental values.


2. MAE (PBE)

Mean lattice constant error compared to PBE data

Same as (1), but optimised lattice constants are compared to reference PBE data.


Computational cost
------------------

Low: tests are likely to less than a minute to run on CPU.


Data availability
-----------------

Input structures:

* Built from experimental lattice constants from various sources

Reference data:

* Experimental data same as input data

* DFT data

  * Batatia, I., Benner, P., Chiang, Y., Elena, A.M., Kovács, D.P., Riebesell, J.,
    Advincula, X.R., Asta, M., Avaylon, M., Baldwin, W.J. and Berger, F., 2025. A
    foundation model for atomistic materials chemistry. The Journal of Chemical
    Physics, 163(18).
  * PBE-D3(BJ)


Elasticity
==========

Summary
-------

Bulk and shear moduli calculated for 12122 bulk crystals from the materials project.


Metrics
-------

(1) Bulk modulus MAE

Mean absolute error (MAE) between predicted and reference bulk modulus (B) values.

MatCalc's ElasticityCalc is used to deform the structures with normal (diagonal) strain
magnitudes of ±0.01 and ±0.005 for ϵ11, ϵ22, ϵ33, and off-diagonal strain magnitudes of
±0.06 and ±0.03 for ϵ23, ϵ13, ϵ12. The Voigt-Reuss-Hill (VRH) average is used to obtain
the bulk and shear moduli from the stress tensor. Both the initial and deformed
structures are relaxed with MatCalc's default ElasticityCalc settings. For more information, see
`MatCalc's ElasticityCalc documentation
<https://github.com/materialsvirtuallab/matcalc/blob/main/src/matcalc/_elasticity.py>`_.

Analysis excludes materials with:
    * B ≤ 0, B > 500 and G ≥ 0, G > 500 structures.
    * H2, N2, O2, F2, Cl2, He, Xe, Ne, Kr, Ar
    * Materials with density < 0.5 (less dense than Li, the lowest density solid element)

(2) Shear modulus MAE

Mean absolute error (MAE) between predicted and reference shear modulus (G) values

Calculated alongside (1), with the same exclusion criteria used in analysis.


Computational cost
------------------

High: tests are likely to take hours-days to run on GPU.


Data availability
-----------------

Input structures:

* 1. De Jong, M. et al. Charting the complete elastic properties of
  inorganic crystalline compounds. Sci Data 2, 150009 (2015).
* Dataset release: mp-pbe-elasticity-2025.3.json.gz from the Materials Project database.

Reference data:

* Same as input data
* PBE


Pressure
========

Summary
-------

Performance when predicting structural properties of bulk crystals under external
pressure (0-150 GPa). Tests the ability to accurately model compression behavior
and bulk moduli derived from pressure-volume relationships.


Metrics
-------

(1) Volume Compression

Mean relative volume compression from 0 to 150 GPa

For each structure, geometry relaxations are performed at multiple pressure points
(0, 10, 30, 50, 100, and 150 GPa) using ASE's StrainFilter with scalar_pressure
parameter. The StrainFilter allows the unit cell to relax under constant external
pressure while maintaining the crystal symmetry. Structures are optimized using
BFGS until forces are below 0.05 eV/Å.

The volume compression metric measures how the crystal volume changes with pressure,
which should show monotonic decrease. This tests whether models can correctly
predict the compressibility of materials.


(2) Bulk Modulus

Mean bulk modulus estimated from pressure-volume data

The bulk modulus (B) is estimated from the pressure-volume relationship using the
derivative B = -V(dP/dV). This provides an alternative measure of elastic
properties compared to the strain-based elasticity benchmark, testing whether
models can reproduce the correct mechanical response to isotropic compression.


Computational cost
------------------

Medium: tests are likely to take minutes to hours to run on CPU/GPU, depending on
the number of structures and pressure points evaluated.


Data availability
-----------------

Input structures:

* Bulk crystal structures from https://alexandria.icams.rub.de/data/pbe/benchmarks/pressure/
* Various crystal types including elements, binary compounds, and more complex materials

Reference data:

* DFT calculations using PBE functional
* Pressure range: 0-150 GPa
* Multiple pressure points for accurate P-V curve construction
