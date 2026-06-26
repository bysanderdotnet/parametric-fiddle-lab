# Architecture Overview

## Pipeline

```
cad/violin.py  ──> violin_body.step, violin_cavity.step, violin_body.json
                      │
                      v
mesh/mesher.py   ──> violin_body.msh, violin_cavity.msh
                      │
     ┌────────────────┴────────────────┐
     v                                 v
sim_struct/structural.py           sim_acoustic/acoustic.py
  (Elmer StressSolve)                (Python P1 FEM)
     │                                 │
     v                                 v
  structural_results.json          acoustic_results.json
     │                                 │
     └────────────────┬────────────────┘
                      v
              opt/optimize.py  (Optuna)
                      │
                      v
               Best parameter set
```

Data flows **cad → mesh → (struct + acoustic) → opt** with intermediate files on disk. Each step is a standalone CLI script.

## Module Responsibilities

### `cad/violin.py`
Parametric violin CAD generator (~110 parameters). Produces STEP (body, cavity) and a JSON manifest (per-part mass, volume, classification). Geometry is an 8-point-polyline outline with cylinder-intersection arching — deliberately simplified.

### `common/params.py`
Single source of truth for all geometry + slicing parameters. Drives both argparse (CLI) and Optuna (search space). Also defines frequency classification thresholds.

### `common/cavity_fem.py`
Pure-Python P1 tetrahedral FEM for acoustic air-cavity eigenmodes. Elmer cannot assemble scalar mass matrices in steady state (tested against v26.2), so this is the fallback. Solves `K f = (omega/c)^2 M f` with `scipy.sparse.linalg.eigsh`.

### `common/elmer.py`
Shared ElmerGrid + ElmerSolver wrapper. Writes SIF files from a template, runs the solver, parses EigenSolve output.

### `mesh/mesher.py`
Gmsh-based STEP-to-tetrahedral-mesh conversion. Assigns physical groups (scroll_tip=1, saddle=2) for structural BCs.

### `sim_struct/structural.py`
Structural eigenmode analysis via Elmer StressSolve. Material from `filaments/bambu_pla_basic.py`. Falls back to dummy results when Elmer or mesh is absent. Also computes max von Mises stress per mm displacement from VTU output.

### `sim_acoustic/acoustic.py`
Air-cavity eigenmode analysis via `common/cavity_fem.py`. Falls back to dummy results. Classifies A0 (Helmholtz), A1, higher modes by frequency thresholds.

### `slice/slicer.py`
Orca Slicer CLI wrapper. Creates a temp working dir, named pipe for progress, invokes orca-slicer with `--slice --export-3mf`, extracts G-code + `slice_info.config` from the 3MF zip.

### `filaments/bambu_pla_basic.py`
Bambu PLA Basic material library with SI convenience fields for FEM (density, Young's modulus, Poisson ratio).

### `opt/objective.py`
Objective function evaluating frequency error (A0, B1-, B1+ targets), mass penalty, missing-data penalty.

### `opt/optimize.py`
Optuna optimization loop (TPE sampler). Each trial runs the full CAD → slice → mesh → FEA pipeline. Prunes failed trials.

## Inter-Module Conventions

- All STEP/MSH/JSON files read/written in CWD.
- Violin long axis = Y. Scroll tip = +Y. Saddle/endpin = -Y.
- Mesh units: mm (Gmsh default). FEM scales to metres via `Coordinate Scaling = 0.001` (Elmer) or `mesh_scale=1e-3` (cavity_fem.py).

## Current Limitations

- Structural eigenfrequencies are not yet physical (near-zero rigid-body modes + spurious ~10^4-10^5 Hz eigenvalues).
- No stress field computed on the Elmer path (VTU parsing is wired but Elmer stress output is unreliable).
- Acoustic FEM targets (A0 ~290 Hz, B1- ~400 Hz, B1+ ~540 Hz) are not calibrated against measured instruments.
- Slicing step skipped when orca-slicer not installed.
