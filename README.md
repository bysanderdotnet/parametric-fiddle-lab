# Parametric Fiddle Lab

Parametric Fiddle Lab is a platform for building a parametric, simulatable, and optimizable design chain for 3D-printed violins. It aims to optimize the acoustic and structural properties of 3D-printed violins by treating geometry, slicing parameters, materials, and internal structure as tunable design variables.

## Overview

The project uses a pipeline architecture:

1. **Parametric Generation:** Generate the geometry from code (CadQuery).
2. **Slicing as Design:** Treat slicing parameters (infill, perimeters, modifiers) as design variables via the Orca Slicer CLI.
3. **Simulation:** Evaluate designs with structural and acoustic simulation (eigenmodes, cavity modes) using Gmsh and Elmer.
4. **Optimization:** Iterate designs with Bayesian optimization (Optuna).

Data flows `cad -> slice -> mesh -> sim_struct / sim_acoustic -> opt`, exchanged through intermediate files (`violin_body.step`, `violin_cavity.step`, `violin_body.json`, `*.msh`, `structural_results.json`, `acoustic_results.json`).

## Directory Structure

* `cad/` - Parametric violin generator (CadQuery); exports STEP + a JSON of per-part volumes and masses
* `common/` - Shared helpers: parameter spec (`params.py`), Elmer SIF/runner (`elmer.py`), acoustic cavity FEM (`cavity_fem.py`)
* `filaments/` - Material property library (currently `bambu_pla_basic`); single source of truth for density/modulus used by CAD mass estimates and FEM
* `mesh/` - STEP-to-mesh conversion via Gmsh
* `slice/` - Orca Slicer CLI wrapper and slice-data export
* `sim_struct/` - Structural simulation: linear-elasticity eigenmodes (Elmer)
* `sim_acoustic/` - Acoustic simulation: air-cavity eigenmodes
* `opt/` - Objective function and Optuna optimization loop
* `scripts/` - Single-parameter sweep scripts and their tests (113 parameters)
* `profiles/` - Orca machine / process / filament profiles (Bambu X1 Carbon 0.4 nozzle)
* `data/` - Run logs, reference curves, benchmark results
* `docs/` - Literature, design notes, parameter reference, decision logs

## Current Status

The Python pipeline runs end-to-end and the full test suite is green
(`./AGENTS.sh verify` -> 131/131 steps). Simulation stages fall back to
randomized dummy results when an external tool or input mesh is missing, so the
pipeline and tests stay green even without the native toolchain installed.

### What works

* **CAD generation** (`cad/violin.py`): generates body, air cavity, bridge,
  soundpost, bass bar, tailpiece, fingerboard, neck, scroll, pegs, chinrest,
  nut, saddle, endpin, and corner/top/bottom blocks. Exports `violin_body.step`,
  `violin_cavity.step`, and `violin_body.json` with per-part volumes and masses.
  Mass estimates use the filament density from `filaments/` (no hardcoded value).
* **Meshing** (`mesh/mesher.py`): Gmsh converts the body and cavity STEP files
  to tetrahedral `.msh` meshes.
* **Structural simulation** (`sim_struct/structural.py`): linear-elasticity
  eigenmodes via Elmer, using material properties from `filaments/`; classifies
  modes as CBR / B1- / B1+ like. Dummy fallback when Elmer or the mesh is absent.
* **Acoustic simulation** (`sim_acoustic/acoustic.py` + `common/cavity_fem.py`):
  air-cavity eigenmodes solved with a custom P1 tetrahedral FEM, including an
  A0-like Helmholtz mode via Dirichlet conditions at the f-holes. Dummy fallback
  when the cavity mesh is absent.
* **Optimization** (`opt/optimize.py`): Optuna drives the full pipeline per
  trial and minimizes the objective in `opt/objective.py`.
* **Parameter sweeps** (`scripts/`): 113 scripts, one per geometry/slicing
  parameter, each with a test.
* **System setup** (`install_sys_deps.sh`): installs Gmsh, Elmer
  (elmer-csc PPA), and OrcaSlicer (AppImage v2.3.2).

### What is partial or not done yet

* **Slicing is wired but not configured.** `slice/slicer.py` wraps the
  `orca-slicer` CLI (its unit tests mock the subprocess), but no real Orca
  profiles are committed — `profiles/` has dummy JSON configs. `opt/optimize.py` and the
  slicing sweep scripts pass a dictionary pointing to these dummy profiles, so the slice
  step is skipped with a warning. Add real machine/process/filament configs to
  `profiles/` to slice for real.
* **Acoustics do not use Elmer.** Elmer's scalar-eigen path does not assemble a
  mass matrix in steady state (upstream limitation, documented in
  `common/cavity_fem.py`), so the Python FEM fallback is the real solver.
* **Structural is eigenanalysis only.** No stress field is computed
  (`max_stress_mpa` is 0 on the Elmer path, 15.4 in the dummy).
* **Geometry is a simplified approximation.** Plate arching is the
  intersection of two circular cylinders (`get_cylinders` in `cad/violin.py`),
  not true graduated violin arching, and there is no recurve, no edge purfling
  channel beyond a single groove, and no plate thickness graduation map — top
  and back are uniform-thickness shells. The body outline is an 8-point
  straight-segment polyline rather than a smooth spline. These are deliberate
  simplifications for a tractable parametric model, not luthier-accurate forms.
* **Strings, pegs, and fine tuners are non-functional.** They are printed
  solid plastic (e.g. 0.5 mm solid "string" cylinders) fused into the body for
  visual completeness — a playable instrument needs real strings, geared or
  friction pegs, and metal fine tuners as hardware, plus a clamp-on chinrest.
  `cad/violin.py` now classifies every part in `violin_body.json`
  (`part_classification`, `non_functional_parts`, and `structural_mass_g` /
  `cosmetic_mass_g`) so the decorative parts are explicit. The printed object is
  a violin-shaped resonating body, not yet a stringable instrument.
* **Structural eigenfrequencies are not yet physical.** The current
  `structural_results.json` contains near-zero rigid-body modes (~0 Hz) and
  spurious high-frequency modes (order 10^4-10^5 Hz), so the B1- / B1+ targets
  in the objective are not meaningful until `sim_struct/structural.py` is
  reviewed for boundary constraints and unit scaling. Acoustic cavity modes are
  in a plausible range; structural modes are not.
* **The objective targets acoustics but is uncalibrated.** `opt/objective.py`
  now makes the A0 / B1- / B1+ frequency errors the dominant term, with mass as
  a single mild regularizer and an explicit penalty for missing simulation
  output (it no longer sums ~20 component masses, which used to swamp the
  acoustic terms). Targets (A0 ~= 290 Hz, B1- ~= 400 Hz, B1+ ~= 540 Hz) are
  still not calibrated against measured instruments.
* **One filament is characterized** (`filaments/bambu_pla_basic.py`). Its
  Poisson ratio is a typical-PLA assumption, not a datasheet value, and the
  referenced datasheet PDF is not committed.
* **`profiles/` contains real Orca profiles** for Bambu X1 Carbon (0.4 nozzle, PLA Basic filament, 0.20mm Standard process). `data/` has literature-based reference measurements for objective calibration (5 violin corpus variants, 143 lines). `docs/` has a complete parameter reference (109 geometry + 2 slicing parameters, mode thresholds, ergonomic constraints).

## Getting Started

Install the native toolchain (Gmsh, Elmer, OrcaSlicer):

```sh
./install_sys_deps.sh
```

Set up the Python environment:

```sh
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```

Run the pipeline stages directly:

```sh
python3 cad/violin.py            # -> violin_body.step, violin_cavity.step, violin_body.json
python3 mesh/mesher.py           # -> violin_body.msh, violin_cavity.msh
python3 sim_struct/structural.py # -> structural_results.json
python3 sim_acoustic/acoustic.py # -> acoustic_results.json
python3 opt/optimize.py --trials 20  # full optimization loop (--trials/--startup-trials/--seed)
```

This repository is managed with an agent harness. Use `./AGENTS.sh help` to see
available project commands, and `./AGENTS.sh verify` to run the full
definition-of-done test suite.
