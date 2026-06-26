# v1.0.4 — 2026-06-26

## What's new since v1.0.3

- **Infill threading** — `infill_pattern` and `wall_loops` are now threaded through the full optimization pipeline. `slice/slicer.py` extracts slice metadata including actual wall count and infill density.
- **Local mesh refinement** — `mesh/mesher.py` supports multi-resolution sizing for structural and acoustic FE meshes, giving finer elements near f-holes and C-bout corners.

## Release artifacts

| File | Description |
|------|-------------|
| `violin_body.step` | Full violin assembly (default params) |
| `violin_cavity.step` | Air cavity for acoustic FEM |
| `violin_body.stl` | STL mesh of full body |
| `violin_body.json` | Per-part volumes, masses, and classification (structural vs cosmetic) |
| `profiles/` | Orca Slicer profile bundle (machine + process + filament) |

### Orca profile bundle

- `profiles/machine.json` — Bambu X1 Carbon, 0.4 nozzle
- `profiles/process.json` — 0.20 mm Standard @ResonantViolin
- `profiles/filament.json` — Bambu PLA Basic @ResonantViolin

See `docs/print-recipe.md` for import and usage instructions.

## Default-parameter output

- Volume: 994,206 mm³
- Estimated mass: 1,233 g (PLA)
- Structural mass: 737 g (excluding cosmetic parts: strings, pegs, fine tuners, chinrest)
- Cavity volume: 1,988,614 mm³
