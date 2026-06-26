# Print Recipe — Resonant Violin Lab

Recommended print settings, part orientation, post-processing, and assembly guide for the parametric 3D-printed violin. Targets Bambu Lab X1 Carbon with 0.4 mm nozzle and PLA Basic filament.

## Hardware Requirements

| Item | Spec |
|------|------|
| Printer | Bambu Lab X1 Carbon (or equivalent 256 mm³ FFF) |
| Nozzle | 0.4 mm hardened steel (stock) |
| Filament | Bambu PLA Basic (or equivalent high-quality PLA) |
| Build plate | Textured PEI (smooth PEI also works) |
| Adhesive | Glue stick or Bambu liquid glue (for smooth PEI) |

Optional: enclosure helps with ASA/PETG/PC prints but is not required for PLA.

## Part Orientation

All parts are designed to print without supports when oriented correctly.

### Body (top + back plate)

**Orientation:** flat on the build plate, exterior face down.

- The plate contour makes full contact with the build surface
- C-bout corners and f-holes overhang < 45° from plate normal
- No support needed for the plate exterior
- Optional: brim (5 mm, 0.2 mm gap) for corner adhesion on textured PEI

### Rib Garlands

**Orientation:** rib profile flat on build plate, interior face up.

- Thin-wall geometry (~2 mm nominal). Ensure wall count ≥ 2 perimeters
- No support needed
- Brim recommended (8 mm) for tall garlands to prevent tip-over

### Neck + Pegbox

**Orientation:** flat side down, fingerboard surface up.

- Neck angle (~5°) creates a gentle overhang. With 0.2 mm layer height
  and 4 perimeters, no support is needed for most profiles
- Pegbox cavity prints cleanly without support due to the chamfered top

### Bridge

**Orientation:** standing upright, string slots up.

- The kidney cutouts and feet are fully self-supporting at 0.2 mm layers
- Brim (5 mm) recommended for the narrow feet

### Soundpost

**Orientation:** standing upright.

- Simple cylinder — no supports, no brim.
- Print at 100% infill for mass consistency.

### Fingerboard

**Orientation:** flat side down, scoop up.

- The scoop radius (42 mm) is gentle enough to bridge without supports
- Bottom face is flat, excellent bed adhesion

### Scroll

**Orientation:** pegbox face down on the build plate.

- The spiral overhangs < 45°; no support needed with 0.2 mm layers
- Brim recommended (6 mm) for the narrow contact area

### Tailpiece, Chinrest, Pegs, Endpin, Nut, Saddle

All flat-bottomed parts that print face-down. No supports. Brim optional
for small-footprint items (endpin, nut, saddle).

## Recommended Print Settings

### PLA (Bambu PLA Basic)

| Setting | Value | Rationale |
|---------|-------|-----------|
| Layer height | 0.20 mm | Best balance of quality and strength |
| First layer | 0.20 mm | Matches subsequent layers |
| Wall loops | 3-4 | Structural parts (body): 4; cosmetic (scroll): 3 |
| Top shells | 4 | Prevents pillowing on large flat surfaces |
| Bottom shells | 4 | Ensures solid base for plate parts |
| Sparse infill | 15-25 % | 15% for body parts, 25% for neck/scroll |
| Infill pattern | gyroid | Isotropic strength, good vibration damping |
| Internal solid infill | rectilinear | Bridges top/bottom shells |
| Skirt loops | 2 | Priming check |
| Brim type | no-brim | Add manual brim for narrow parts |
| Support | none | Parts designed support-free at 0.2 mm |
| Build plate adhesion type | skirt | Default; use brim manually per part notes |

### Advanced Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Avoid crossing wall | on | Reduces stringing on thin walls (f-holes, bridge) |
| Detect thin walls | on | Ensures rib garlands and f-hole bridges print |
| Filter out tiny gaps | on | Clean top surfaces over thin features |
| Overhang walls | 5 | Ensures gentle overhang bridges print cleanly |
| Wall generator | Arachne | Better thin-wall handling for ribs and f-holes |
| Seam position | aligned | Cleanest visual appearance for body parts |
| Scarf joint seam | on | Reduces visible seam on curved contours |
| Precision | 0.01 mm | Default; fine enough for part fit |
| Fuzzy skin | off | Kosmetically unnecessary for violin body |

### Support Filament Settings (PETG / ASA / PC / Nylon-CF)

See [filament characterization notes](../filaments/) for individual profiles.
General guidance:

| Setting | PETG | ASA | PC | Nylon-CF |
|---------|------|-----|----|----------|
| Bed temp | 75 °C | 90 °C | 100 °C | 60 °C (garolite) |
| Nozzle temp | 240 °C | 260 °C | 270 °C | 280 °C |
| Chamber | off | 50 °C | 60 °C | 60 °C |
| Enclosure | optional | required | required | required |
| Drying | 65 °C 8h | 80 °C 8h | 90 °C 8h | 80 °C 8h |
| Layer height | 0.20 mm | 0.20 mm | 0.20 mm | 0.16 mm |
| Wall loops | 4 | 4 | 5 | 4 |
| Infill | 25% | 25% | 30% | 25% |

All require brim on narrow-contact parts. ASA/PC/Nylon-CF require active
chamber heating and enclosure. PETG may show stringing on f-holes — enable
`avoid crossing wall` and slow print speed.

## Post-Processing

### Support Removal

No supports required for the designed orientations. If you enable supports
for a modified part: use snug supports with 0.2 mm z-gap and organic
interface pattern. Remove carefully from f-hole interior (brittle).

### Surface Finishing

| Part | Treatment | Notes |
|------|-----------|-------|
| Top plate | Light sanding 400→1000 grit | Remove layer lines around arching |
| Back plate | As printed or sanded | Cosmetic only |
| Ribs | Sand inside seam | Finger-joint or glue seam |
| Neck | Sand 400→1000 grit | Playability surface; must be smooth |
| Fingerboard | Sand 400→2000 grit | Critical for playability; polish to satin |
| Bridge | Light sanding 400→600 grit | Clean kidney cutouts and feet |
| Scroll | Minimal sanding | Detail preservation; hand-sand spiral |

**PLA post-processing** (optional): vapor smoothing with ethyl acetate
(or specialized PLA smooth/gloss coatings). Test on scrap first — vapor
smoothing can soften fine detail (f-holes, purfling groove).

### Hole Finishing

| Hole | Post-process | Tool |
|------|-------------|------|
| Peg holes | Ream to taper + fine sand | Peg reamer or round file |
| Endpin hole | Drill 4.5 mm + sand | 4.5 mm bit, then sand |
| Fine tuner holes | Drill 2.5 mm | 2.5 mm bit |
| String holes (bridge) | Clean with 1 mm drill | Hand-twist; do not power-drill |

**Note:** print orientation produces slightly undersized holes due to
elephant's foot and layer stepping. Always drill/ream to final size.

### Assembly

#### Order of assembly
1. **Soundpost** — place inside body between top/back (use soundpost setter)
2. **Bass bar** — if printed separately, glue to underside of top plate
3. **Top plate** — glue ribs + corner blocks to top plate
4. **Back plate** — glue ribs + corner blocks to back plate
   (If printing as one-piece body, skip 3-4; the full body is monolithic)
5. **Neck** — glue into neck mortise at 5° angle
6. **Fingerboard** — glue to neck top surface, align to center
7. **Pegs** — insert through pegbox holes; ream to fit
8. **Nut** — glue at top of fingerboard; file string grooves
9. **Bridge** — stand on top plate between f-holes; tension strings hold it
10. **Tailpiece** — attach via tailgut (printed or nylon cord) to endpin
11. **Strings** — ball end → tailpiece, peg end → peg; tune to pitch
12. **Chinrest** — clamp to body edge below tailpiece
13. **Endpin** — insert and tighten

#### Adhesives

| Joint | Adhesive | Notes |
|-------|----------|-------|
| Ribs ↔ plates | CA (cyanoacrylate) gel | Medium-thick; gap-filling |
| Neck ↔ body | Epoxy (5-min) | Structural joint; clamp 30 min |
| Fingerboard ↔ neck | CA gel or epoxy | CA for quick, epoxy for strength |
| Nut / saddle | CA thin | Small parts; wick into joint |
| Bass bar | CA gel or epoxy | Structural; clamp firmly |
| Soundpost | Friction-fit only | Must be removable for adjustment |

### Stringing

Standard violin string set (4 strings):

| String | Pitch | Note |
|--------|-------|------|
| G3 | 196 Hz | Wound |
| D4 | 293.66 Hz | Wound or plain |
| A4 | 440 Hz | Plain |
| E5 | 659.25 Hz | Plain (may use fine tuner) |

Tuning sequence: G → D → A → E. Let strings stretch for 24-48 hours before
final tuning. Expect to re-tune multiple times during the first session.

## Orca Profile Bundle

The profiles in `profiles/` are pre-configured for Bambu X1 Carbon with
0.4 mm nozzle and Bambu PLA Basic filament.

To use:
1. Copy `machine.json`, `process.json`, `filament.json` into your Orca
   Slicer user profiles directory:
   - Linux: `~/.config/OrcaSlicer/user/`
   - macOS: `~/Library/Application Support/OrcaSlicer/user/`
   - Windows: `%APPDATA%/OrcaSlicer/user/`
2. Restart Orca Slicer
3. Select "Bambu Lab X1 Carbon 0.4 nozzle" as printer
4. Select "0.20mm Standard @ResonantViolin" as process
5. Select "Bambu PLA Basic @ResonantViolin" as filament
6. Load `.step` or `.stl` and slice

For advanced slicing (bridge, infill pattern, wall count changes), modify
the `process.json` before importing, or use the Orca overrides after slicing.

### What each profile contains

| File | Scope | Key settings |
|------|-------|-------------|
| `machine.json` | Printer definition | Build volume 256x256x256, max vol speed 21 mm³/s, Klipper firmware, start/end gcode, Z-hop, retraction 0.8 mm / 30 mm/s, bed 55-65 °C |
| `process.json` | Print parameters | 0.2 mm layer height, 3-4 walls, 15% gyroid infill, Arachner wall gen, scarf joints, avoid crossing walls, no support, 200 mm/s outer wall, 300 mm/s infill |
| `filament.json` | Material settings | Bambu PLA Basic, 1.75 mm, 220-230 °C nozzle, 55-65 °C bed, 0.98 flow ratio, 21 mm³/s max vol speed, pressure advance 0.02 |

### Customization for other printers

The profiles assume a 256 mm³ build volume, 0.4 mm nozzle, and direct-drive
extruder. For other printers, adjust in `machine.json`:
- `printable_area`, `printable_height` — build volume
- `nozzle_diameter`, `nozzle_type` — nozzle spec
- `machine_start_gcode`, `machine_end_gcode` — printer-specific gcode
- `retraction_length`, `retraction_speed` — bowden vs direct drive
- `max_acceleration_*`, `max_speed_*` — printer kinematic limits

## Export Formats

### .step (Recommended)

Use for slicing. Preserves parametric exact geometry (BREP) for Orca Slicer.
Export from `cad/violin.py` by setting `export_format="step"`.

### .stl (Fallback)

Use for unsliced viewing or when STEP export is unavailable. Coarse tessellation
(default 0.01 mm chordal tolerance) may inflate file size. Fine for slicing.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Warped corners on top plate | Insufficient brim / bed adhesion | Add 8 mm brim; clean plate with IPA; reapply glue |
| Stringing on f-hole interior | Retraction too low | Increase retraction 0.8→1.0 mm; enable avoid crossing walls |
| Layer shift on tall parts | Part tip-over | Add brim; slow outer wall speed; check belt tension |
| First layer gaps on rib garlands | Elephant's foot / z-offset | Adjust first layer extrusion width to 0.42 mm |
| Bridge feet don't fit body curvature | Print orientation drift | Re-slice with aligned seam; verify z-scale |
| Peg holes too tight or too loose | Layer stepping tolerance | Ream to 3.0 mm (tight) or 3.2 mm (loose); use peg compound |
| Back plate buzzing at A0 frequency | Insufficient infill coupling | Increase infill density to 25%; verify gyroid pattern |
| F-holes have drooping bridges | Overhang > 45° at some features | Enable overhang wall speed reduction (5 mm threshold) |

## STEP File Export

The latest stable `.step` release is `v1.0.4`. See [releases](../releases/)
for the bundled export archive including the `.step` file and matching Orca
profile bundle.

To generate a fresh `.step` from current parameters:
```bash
python cad/violin.py --export step --output violin_v1.step
```

The export will produce a complete violin assembly including body, neck,
fingerboard, bridge, soundpost, tailpiece, chinrest, pegs, endpin, nut,
and saddle.
