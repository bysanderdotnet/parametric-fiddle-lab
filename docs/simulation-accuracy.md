# Simulation Accuracy Decision Log

This document tracks architectural decisions, known fidelity gaps, and planned mitigations in the simulation chain.

## 1. Structural Frequencies Are Unphysical

**Status:** Open. Structural eigenfrequencies from Elmer do not match real violin modes.

### Observed behavior
- Near-zero rigid-body modes (the 6 rigid DOFs) appear at single-digit Hz despite clamped BCs.
- Physical bending/twisting modes appear at 10^4–10^5 Hz — 100x higher than a real violin's corpus modes (~200–800 Hz).
- No stress field is reliably computed (VTU parsing falls through).

### Likely root causes
1. **Material stiffness.** PLA has E ≈ 2.58 GPa. Spruce (violin top) is ~10 GPa along grain, ~0.5 GPa across. Maple (back) is ~12 GPa along grain, ~1 GPa across. PLA's isotropic modulus is in the right ballpark, but:
   - PLA is isotropic and homogeneous; wood is strongly orthotropic and graded.
   - The 3D-printed nature introduces anisotropy between in-plane (X-Y) and layer (Z) directions, which the isotropic Elmer model does not capture.
2. **Geometry fidelity.** The body is a simplified 8-point polyline with uniform-thickness plates and cylinder-intersection arching. Real violin graduations are 2.5–4.5 mm varying continuously. These simplifications stiffen the structure.
3. **Boundary conditions.** Clamping the scroll tip and saddle over-constrains the free-free violin body. Physically, the corpus is held at the neck and by string tension — not rigidly clamped.
4. **Mesh quality.** Gmsh's default mesh size (5.0 mm) produces ~10k tets for the violin body — too coarse for resolving bending modes with sub-mm displacements.

### Planned mitigations
- Refine BCs: use spring constraints or free-free instead of clamped.
- Add mesh refinement study (1.0, 2.0, 5.0 mm sizes).
- Validate against analytical plate formulas (e.g., simply-supported rectangular plate modes) before trusting violin body output.
- Introduce orthotropic material properties once Elmer's material model supports them.
- Consider Code_Aster as an alternative to Elmer for structural eigenanalysis.

## 2. Acoustic FEM: Python P1 Fallback vs Elmer

**Status:** Wired and producing plausible dummy values. Real FEM path needs validation.

### Decision: Use Python P1 scalar FEM for cavity modes
- Elmer's HeatSolve/HelmholtzSolve cannot assemble scalar mass matrices in steady state (tested 2026-06-15 against PPA 26.2 and source build 26.2.1). StressSolve works because elasticity always builds a mass matrix.
- The Python fallback in `common/cavity_fem.py` assembles P1 tetrahedral FEM directly, solves with `scipy.sparse.linalg.eigsh`.

### Known gaps
1. **A0 Helmholtz mode.** Dirichlet BCs (P=0) at f-hole surface nodes approximate the pressure-release opening, but:
   - The f-holes are not physically coupled to external radiation impedance.
   - The cavity mesh's f-hole region may be too coarse for accurate A0 frequency.
   - A0 formula: `f_A0 = (c/2π) * sqrt(S / (V * L_eff))`. The FEM should converge to this for simple spherical cavities — validate.
2. **Radiation efficiency.** Not computed. Vibroacoustic coupling (structural → acoustic) requires a coupled solver not yet in the pipeline.
3. **Damping.** No viscothermal or radiation damping is modeled. Mode widths (Q factors) are unavailable.
4. **F-hole profile accuracy.** The `is_in_f_hole` function uses an `(rx, ry)` rectilinear approximation rotated by `f_hole_angle`. Curved classic f-hole eyes use circle intersections but the slot-body region is rectangular — this is a geometric simplification.

### Mitigation plan
- Benchmark against analytical Helmholtz resonator formula.
- Validate P1 FEM convergence with mesh refinement.
- Eventually add Elmer custom solver or couple with external BEM for radiation.

## 3. Objective Function: Weight Tuning

**Status:** Tuned. Frequency error dominates; mass is a mild regularizer.

### Decision history
- **v0.1:** Summed ~20 component masses at weight 5.0 each. Mass penalty dwarfed frequency error (~100x). Optimizer shrank every part.
- **v0.2:** Single `mass_g` at weight `MASS_WEIGHT = 0.05`. Still too strong (~20 pts for 400 g vs ~100 pts for 100 Hz error).
- **v0.3 (current):** `MASS_WEIGHT = 0.05`, `MISSING_DATA_PENALTY = 1000.0`. Mass penalty is now ~20 pts for a typical body. Frequency error typically runs 100–500 pts. Missing data penalty ensures failed trials can't score well.

### Target frequencies
- **A0:** 290 Hz — approximate Helmholtz resonance of a violin cavity (~1.9 L, ~90 mm² f-hole area). Not yet calibrated.
- **Structural (B1-):** 400 Hz — typical violin B1- mode. Uncalibrated for PLA.
- **B1+:** 540 Hz — typical violin B1+ mode. Uncalibrated for PLA.

Planned: replace with corpus-specific targets from a reference scan.

## 4. Slicer Integration

**Status:** Wired but inactive. `orca-slicer` is absent in most dev environments; the step is skipped with a warning.

### Key parameters transferred to slicer
- `infill_density` → `--sparse-infill-density`
- `layer_height` → `--layer-height`

These are the two slicing parameters in the Optuna search space. Expanding the slicing search space (wall count, infill pattern, top/bottom layers) is deferred until the structural/acoustic pipeline is calibrated.

### Orca profiles
Real Bambu Lab X1 Carbon profiles are committed in `profiles/`. They are loaded by path but the slicer is never called in a standard `pytest` run.

## 5. Mesh Quality

**Status:** Default 5.0 mm characteristic length. No mesh convergence study performed.

Typical element counts:
- `violin_body.msh`: ~10k tets
- `violin_cavity.msh`: ~4k tets

For acoustic P1 FEM, the rule of thumb is 10 elements per wavelength. At 500 Hz (lambda_air ≈ 0.69 m), element size should be ≤70 mm — so the cavity mesh is adequate for A0/A1. For structural bending modes with sub-millimeter wavelengths in thin plates, 5.0 mm tets are likely too coarse.

## 6. Boundary Condition Fidelity

**Status:** Clamped BCs on scroll tip and saddle. Not realistic for a free violin body.

Real violins are held at the neck (by the player's hand) and by string tension (bridge → tailpiece → endpin). The body itself is free to vibrate. Clamping at two extreme points over-constrains the body and shifts mode shapes.

Planned: switch to free-free BCs (remove all clamped BCs; let Elmer's solver handle rigid-body modes by ignoring <1 Hz eigenvalues in classification).
