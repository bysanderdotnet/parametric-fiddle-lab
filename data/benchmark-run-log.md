# Benchmark Run Log

## Baseline: v0.3 (2026-06-26)

### Environment
- Python 3.13.5
- Elmer: not installed (CI environment)
- Orca Slicer: not installed
- Gmsh: not installed

### Test Suite (no CadQuery/Gmsh/Elmer)
```
$ python3 -m pytest common/test_params.py common/test_elmer.py opt/test_objective.py --tb=short
13 passed in 0.12s
```

### Pipeline: Dummy Fallback Mode
Ran each step independently (no Elmer, no Gmsh, no Orca). All steps fell through to their dummy fallback paths.

#### CAD
`cad/violin.py` requires CadQuery + OCC — skipped. No violin_body.step or violin_body.json generated.

#### Mesh
`mesh/mesher.py` requires Gmsh — skipped. No .msh files.

#### Structural Simulation
`sim_struct/structural.py --mesh violin_body.msh` — mesh absent → dummy results:
- Mode 1: ~280 Hz (CBR-like)
- Mode 2: ~400 Hz (B1- like)
- Mode 3: ~530 Hz (B1+ like)
- Mass: 400 g (default)
- Max stress: 1150 MPa (dummy placeholder — unphysical)

#### Acoustic Simulation
`sim_acoustic/acoustic.py --mesh violin_cavity.msh` — mesh absent → dummy results:
- Mode 1: ~290 Hz (A0-like Helmholtz)
- Mode 2: ~450 Hz (A1-like)
- Radiation efficiency: 0.1–0.3 (randomized dummy)

#### Optimization
`opt/optimize.py --trials 5` — requires CadQuery. Not run.

### Test Counts
- Total test functions: ~153 (all tests)
- Tests passing without CadQuery/Elmer: 13
- Tests requiring CadQuery: ~140 (cad/, scripts/sweep_*, scripts/test_*.py)

### Key Baseline Numbers (Dummy)
| Metric | Value | Unit |
|--------|-------|------|
| A0 target | 290 | Hz |
| B1- target | 400 | Hz |
| B1+ target | 540 | Hz |
| Default mass | 400 | g |
| Mass penalty weight | 0.05/g | — |
| Missing data penalty | 1000 | per source |
| Default structural mesh size | 5.0 | mm |
| Expected ~10k tets / ~4k tets | body / cavity | — |

### Next Benchmark Targets
1. Run with CadQuery + Gmsh + full dependency stack
2. Run with Elmer installed and mesh generated
3. 20-trial Optuna run with all four pipeline steps enabled
4. Mesh convergence study (1.0, 2.0, 5.0 mm)
