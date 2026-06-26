# Parameter Reference

109 geometry + 2 slicing parameters are defined in `common/params.py` (SPEC list). Each entry specifies name, type (float/str/bool), optimization range or choices, and help text.

## Geometry Parameters (107)

| # | Name | Type | Range / Choices | Default | Description |
|---|------|------|-----------------|---------|-------------|
| 1 | length | float | 340-370 mm | 355.0 | Body length |
| 2 | lower_bout | float | 200-220 mm | 208.0 | Lower bout width |
| 3 | upper_bout | float | 160-180 mm | 168.0 | Upper bout width |
| 4 | c_bout | float | 100-120 mm | 110.0 | C-bout waist width |
| 5 | top_thickness | float | 2-6 mm | 4.0 | Top plate thickness |
| 6 | back_thickness | float | 2-6 mm | 4.0 | Back plate thickness |
| 7 | rib_thickness | float | 2-6 mm | 4.0 | Rib thickness |
| 8 | top_arch_height | float | 10-25 mm | 15.0 | Top plate arch height |
| 9 | back_arch_height | float | 10-25 mm | 15.0 | Back plate arch height |
| 10 | rib_height | float | 25-40 mm | 30.0 | Rib height |
| 11 | f_hole_length | float | 60-90 mm | 70.0 | F-hole length |
| 12 | f_hole_spacing | float | 60-100 mm | 80.0 | F-hole spacing |
| 13 | f_hole_width | float | 5-12 mm | 8.0 | F-hole slot width |
| 14 | f_hole_thickness | float | 1-5 mm | 2.0 | F-hole edge reinforcement thickness |
| 15 | f_hole_profile | str | slot, classic | slot | F-hole profile shape |
| 16 | f_hole_top_radius | float | 3-6 mm | 4.0 | Top eye radius (classic) |
| 17 | f_hole_bottom_radius | float | 3-6 mm | 5.0 | Bottom eye radius (classic) |
| 18 | f_hole_x_offset | float | -20-20 mm | 0.0 | F-hole x-offset |
| 19 | f_hole_y_offset | float | -20-20 mm | 0.0 | F-hole y-offset |
| 20 | f_hole_angle | float | 75-105 deg | 90.0 | F-hole rotation angle |
| 21 | neck_length | float | 110-150 mm | 130.0 | Neck length |
| 22 | neck_width_top | float | 20-30 mm | 24.0 | Neck width at nut |
| 23 | neck_width_bottom | float | 30-40 mm | 34.0 | Neck width at body joint |
| 24 | neck_thickness | float | 15-30 mm | 20.0 | Neck thickness |
| 25 | neck_angle | float | 2-8 deg | 5.0 | Neck set angle |
| 26 | bridge_width_bottom | float | 35-45 mm | 40.0 | Bridge bottom width |
| 27 | bridge_width_top | float | 25-35 mm | 30.0 | Bridge top width |
| 28 | bridge_height | float | 20-40 mm | 30.0 | Bridge height |
| 29 | bridge_thickness | float | 3-8 mm | 5.0 | Bridge thickness |
| 30 | bridge_radius | float | 15-40 mm | 20.0 | Bridge top curvature radius |
| 31 | bridge_inner_curve_radius | float | 5-15 mm | 8.0 | Bridge inner side curve radius |
| 32 | bridge_side_cutout_radius | float | 3-10 mm | 6.0 | Bridge side cutout radius |
| 33 | bridge_cutout_radius | float | 2-8 mm | 5.0 | Bridge kidney cutout radius |
| 34 | bridge_cutout_y_offset | float | 5-20 mm | 10.0 | Bridge cutout vertical offset |
| 35 | bridge_central_cutout | bool | True, False | True | Include central heart cutout |
| 36 | bridge_central_cutout_radius | float | 2-8 mm | 4.0 | Central cutout radius |
| 37 | bridge_central_cutout_inner_radius | float | 1-5 mm | 2.0 | Central cutout inner radius |
| 38 | bridge_central_cutout_y_offset | float | 10-25 mm | 15.0 | Central cutout vertical offset |
| 39 | bridge_foot_length | float | 5-15 mm | 10.0 | Bridge foot length |
| 40 | bridge_foot_width | float | 3-10 mm | 5.0 | Bridge foot thickness |
| 41 | bridge_foot_height | float | 2-10 mm | 5.0 | Bridge foot arch height |
| 42 | bridge_foot_cutout_width | float | 2-8 mm | 4.0 | Foot cutout arch width |
| 43 | bridge_foot_cutout_height | float | 1-5 mm | 2.0 | Foot cutout arch height |
| 44 | bridge_cutouts | bool | True, False | True | Enable bridge kidney cutouts |
| 45 | bridge_y_offset | float | -20-20 mm | 0.0 | Bridge y-position offset |
| 46 | bridge_angle | float | -15-15 deg | 0.0 | Bridge rotation angle |
| 47 | soundpost_thickness | float | 4-10 mm | 6.0 | Soundpost diameter |
| 48 | soundpost_length | float | 30-70 mm | 50.0 | Soundpost length |
| 49 | soundpost_x_offset | float | 5-25 mm | 15.0 | Soundpost x-offset from center |
| 50 | soundpost_y_offset | float | -25--5 mm | -15.0 | Soundpost y-offset |
| 51 | bass_bar_length | float | 150-250 mm | 200.0 | Bass bar length |
| 52 | bass_bar_width | float | 3-8 mm | 5.0 | Bass bar width |
| 53 | bass_bar_height | float | 5-15 mm | 10.0 | Bass bar height |
| 54 | bass_bar_x_offset | float | -25--5 mm | -15.0 | Bass bar x-offset |
| 55 | bass_bar_y_offset | float | -20-20 mm | 0.0 | Bass bar y-offset |
| 56 | bass_bar_angle | float | -15-15 deg | 0.0 | Bass bar rotation angle |
| 57 | tailpiece_length | float | 100-120 mm | 110.0 | Tailpiece length |
| 58 | tailpiece_width_top | float | 30-45 mm | 40.0 | Tailpiece top width |
| 59 | tailpiece_width_bottom | float | 15-25 mm | 20.0 | Tailpiece bottom width |
| 60 | tailpiece_thickness | float | 3-8 mm | 5.0 | Tailpiece thickness |
| 61 | tailpiece_y_offset | float | -20-20 mm | 0.0 | Tailpiece y-offset |
| 62 | purfling_groove_depth | float | 0.5-2 mm | 1.0 | Purfling groove depth |
| 63 | purfling_groove_width | float | 0.5-2 mm | 1.0 | Purfling groove width |
| 64 | purfling_groove_offset | float | 1-4 mm | 2.0 | Purfling inset from edge |
| 65 | fingerboard_length | float | 250-290 mm | 270.0 | Fingerboard length |
| 66 | fingerboard_width_top | float | 22-26 mm | 24.0 | Fingerboard width at nut |
| 67 | fingerboard_width_bottom | float | 40-44 mm | 42.0 | Fingerboard width at bridge |
| 68 | fingerboard_thickness | float | 4-7 mm | 5.0 | Fingerboard thickness |
| 69 | fingerboard_radius | float | 30-60 mm | 42.0 | Fingerboard scoop radius |
| 70 | fingerboard_end_shape | str | flat, curve | flat | Fingerboard end shape |
| 71 | pegbox_length | float | 65-75 mm | 70.0 | Pegbox length |
| 72 | pegbox_width | float | 22-26 mm | 24.0 | Pegbox width |
| 73 | pegbox_depth | float | 18-22 mm | 20.0 | Pegbox depth |
| 74 | pegbox_thickness | float | 4-6 mm | 5.0 | Pegbox wall thickness |
| 75 | pegbox_angle | float | 0-15 deg | 5.0 | Pegbox back angle |
| 76 | peg_hole_radius | float | 2.5-3.5 mm | 3.0 | Peg hole radius |
| 77 | peg_spacing | float | 14-16 mm | 15.0 | Peg hole spacing |
| 78 | peg_length | float | 35-55 mm | 40.0 | Peg length |
| 79 | peg_width | float | 15-25 mm | 20.0 | Peg head width |
| 80 | peg_head_length | float | 10-30 mm | 15.0 | Peg head length |
| 81 | peg_head_thickness | float | 3-10 mm | 5.0 | Peg head thickness |
| 82 | endpin_length | float | 15-25 mm | 20.0 | Endpin length |
| 83 | endpin_radius | float | 3-6 mm | 4.0 | Endpin radius |
| 84 | nut_length | float | 3-8 mm | 5.0 | Nut length |
| 85 | nut_width | float | 22-26 mm | 24.0 | Nut width |
| 86 | nut_height | float | 5-10 mm | 8.0 | Nut height |
| 87 | saddle_length | float | 3-8 mm | 5.0 | Saddle length |
| 88 | saddle_width | float | 25-35 mm | 30.0 | Saddle width |
| 89 | saddle_height | float | 4-8 mm | 6.0 | Saddle height |
| 90 | scroll_radius | float | 8-12 mm | 10.0 | Scroll spiral radius |
| 91 | scroll_width | float | 18-22 mm | 20.0 | Scroll width |
| 92 | chinrest_x_offset | float | -60--20 mm | -40.0 | Chinrest x-offset |
| 93 | chinrest_y_offset | float | -160--120 mm | -140.0 | Chinrest y-offset |
| 94 | chinrest_width | float | 60-100 mm | 80.0 | Chinrest width |
| 95 | chinrest_length | float | 40-70 mm | 55.0 | Chinrest length |
| 96 | chinrest_height | float | 10-25 mm | 18.0 | Chinrest height |
| 97 | fine_tuner_radius | float | 1-4 mm | 2.5 | Fine tuner radius |
| 98 | fine_tuner_height | float | 4-15 mm | 10.0 | Fine tuner height |
| 99 | fine_tuner_y_offset | float | -10-10 mm | 0.0 | Fine tuner y-offset |
| 100 | chinrest_cutout_radius | float | 40-80 mm | 60.0 | Chinrest cup radius |
| 101 | chinrest_cutout_depth | float | 2-10 mm | 5.0 | Chinrest cup depth |
| 102 | c_bout_cutout_radius | float | 30-60 mm | 45.0 | C-bout corner radius |
| 103 | c_bout_height | float | 40-80 mm | 60.0 | C-bout cutout height |
| 104 | top_block_width | float | 30-60 mm | 45.0 | Top block width |
| 105 | top_block_length | float | 10-30 mm | 20.0 | Top block length |
| 106 | bottom_block_width | float | 30-60 mm | 45.0 | Bottom block width |
| 107 | bottom_block_length | float | 10-30 mm | 20.0 | Bottom block length |
| 108 | corner_block_width | float | 10-30 mm | 20.0 | Corner block width |
| 109 | corner_block_length | float | 10-30 mm | 20.0 | Corner block length |

## Slicing Parameters (2)

| # | Name | Type | Range / Choices | Default | Description |
|---|------|------|-----------------|---------|-------------|
| 110 | infill_density | float | 5-100% | 15 | Sparse infill density |
| 111 | layer_height | float | 0.08-0.28 mm | 0.2 | Layer height |

## Target Frequencies (not optimized)

| Name | Default | Description |
|------|---------|-------------|
| target_a0_freq | 290.0 Hz | Target A0 Helmholtz cavity mode |
| target_b1_minus_freq | 400.0 Hz | Target B1- structural mode |
| target_b1_plus_freq | 540.0 Hz | Target B1+ structural mode |

## Mode Classification Thresholds

Set in `common/params.py`:

| Constant | Value | Description |
|----------|-------|-------------|
| FREQ_CBR_MAX | 340.0 Hz | CBR-like upper bound |
| FREQ_B1_MINUS_MAX | 465.0 Hz | B1- like upper bound |
| FREQ_A0_MAX | 350.0 Hz | A0 (Helmholtz) upper bound |
| FREQ_A1_MAX | 550.0 Hz | A1 cavity mode upper bound |

## Ergonomic and Playability Constraints

Defined in `common/constraints.py`. Each constraint is validated independently
and reports a human-readable violation message. The `validate(params)` entry
point runs all checks and returns a list of violations (empty = all pass).

### Neck width (left-hand reach)

| Constraint | Min (mm) | Max (mm) | Why |
|------------|----------|----------|-----|
| `neck_width_top` | 22.0 | 27.0 | Too narrow -> cramped spacing; too wide -> small hands can't reach |
| `neck_width_bottom` | 32.0 | 38.0 | Too narrow -> feels unstable; too wide -> reach compromised |

### String spacing

Derived as `neck_width_top / 3` (nut) and `bridge_width_bottom / 3` (bridge).

| Location | Min (mm) | Max (mm) | Why |
|----------|----------|----------|-----|
| Nut | 5.5 | 8.5 | Too close -> imprecise fingering; too far -> awkward chord shapes |
| Bridge | 8.0 | 14.5 | Too close -> unclear bowing; too far -> bow-arm strain |

Also enforced: bridge spacing must exceed nut spacing (strings fan outward).

### Scale length

Nut-to-bridge vibrating string distance. Computed as:

    scale = body_length / 2 + neck_length - bridge_y_offset

| Min (mm) | Max (mm) | Why |
|----------|----------|-----|
| 310.0 | 335.0 | Full-size 4/4 violin target (~328-330 mm standard) |

### Fingerboard curvature

| Constraint | Min (mm) | Max (mm) | Why |
|------------|----------|----------|-----|
| `fingerboard_radius` | 36.0 | 50.0 | Too curved -> single-string fingering awkward; too flat -> double stops unstable |

42 mm is the standard violin medium radius.

### Bow clearance at C-bout corners

The bow can hit the upper/lower bout corners when bowing outer strings (E and G).
Clearance = `min(upper_bout, lower_bout) / 2 - bridge_width_bottom / 2`.

| Min (mm) | Why |
|----------|-----|
| 5.0 | Bow diameter is ~5-6 mm; less clearance means bow hits the C-bout corner |

### Key findings from default parameters

Running `validate()` on the CAD defaults (`cad/violin.py` defaults) reveals:

1. **Scale length (307.5 mm)** is below the 310 mm minimum for full-size. This is
   because the default bridge is at y=0 (body center) while the nut is at
   y = 177.5 + 130 = 307.5. A more realistic bridge position with a negative
   y_offset (toward the tailpiece) or a longer neck would resolve this.
2. All other constraint categories (neck width, string spacing, fingerboard
   curvature, bow clearance) pass at the default parameter set.
