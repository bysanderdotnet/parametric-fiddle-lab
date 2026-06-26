# Orca Slicer Profiles

Real Orca Slicer v2.3.2 system preset configurations for the
Bambu Lab X1 Carbon (0.4mm nozzle, PLA Basic).

| File | Fields | Category |
|---|---|---|
| `machine.json` | 136 | Printer kinematics, limits, gcode macros, probes, toolhead |
| `process.json` | 381 | Layer, perimeters, infill, speeds, cooling, supports, ironing, wipe |
| `filament.json` | 97 | PLA material properties, temperature, fan curve, pressure advance |

Cross-referenced via `compatible_printers` / `setting_id` — all three load
together via the Orca Slicer CLI `--load-settings` / `--load-filaments` flags
(see `slice/slicer.py`).
