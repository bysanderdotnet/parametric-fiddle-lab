# Orca Slicer CLI reference for automated slicing

This note summarizes the Orca Slicer command-line interface for use in this repository's slicing pipeline.

Source basis: Printago's “Orca Slicer CLI: The Complete Reference for Headless Slicing”, published 2026-04-16, based on `orca-slicer --help` for Orca Slicer 2.3.2 and production headless slicing experience. Treat this as a practical third-party reference, not as a stable upstream contract. Pin the Orca Slicer version used by the project and re-run `orca-slicer --help` after upgrades.

## Why this matters here

`parametric-fiddle-lab` treats slicing as part of the instrument design space, not just as a final export step. Orca Slicer can be driven headlessly, which makes it useful for:

- batch slicing generated violin/fiddle geometry;
- varying slicer settings such as layer height, walls, infill, support, seam placement, and modifiers;
- exporting `.gcode.3mf` artifacts that can be inspected, simulated, costed, or printed;
- collecting repeatable metadata such as filament usage, estimated print time, resolved settings, and layer count.

## Typical headless invocation

```bash
orca-slicer \
  --slice 1 \
  --load-settings "profiles/machine.json;profiles/process.json" \
  --load-filaments "profiles/filament_pla.json" \
  --allow-newer-file \
  --min-save \
  --debug 2 \
  --export-3mf runs/example/output.gcode.3mf \
  cad/out/fiddle.3mf
```

Important points:

- `--slice 1` slices plate 1. `--slice 0` slices all plates.
- `--export-3mf` writes a `.gcode.3mf` archive, not a plain `.gcode` file.
- `--load-settings` is semicolon-separated. Use machine settings first, then process settings.
- `--load-filaments` is semicolon-separated, one filament profile per slot.
- `--allow-newer-file` is useful in automation when generated or edited 3MF files may carry a newer version marker.
- `--min-save` keeps output artifacts smaller.

## Core flags

### Input and profile loading

| Flag | Use |
|---|---|
| `--datadir <path>` | Use a separate Orca settings directory. Helpful for CI, experiments, and isolated profile sets. |
| `--load-settings "machine.json;process.json"` | Load machine and process profiles. Order matters. |
| `--load-filaments "filament1.json;filament2.json"` | Load filament profiles by slot. |
| `--load-filament-ids "1,2,3"` | Map objects to filament slots. |
| `--load-assemble-list <file.json>` | Build a plate from a JSON list of models, counts, positions, and filament assignments. Useful when the pipeline produces separate STL/3MF parts. |
| `--load-custom-gcodes <file.json>` | Load custom G-code snippets, such as toolchange G-code. |
| `--load-slicedata <directory>` | Reuse cached slicing data where possible. |
| `--allow-newer-file` | Accept a 3MF saved by a newer Orca Slicer version. |
| `--skip-modified-gcodes` | Ignore modified printer or filament G-code embedded in the 3MF. |
| `--uptodate` | Update configuration values in the 3MF. |
| `--uptodate-settings "machine.json;process.json"` | Settings used together with `--uptodate`. |
| `--uptodate-filaments "filament1.json;..."` | Filament profiles used together with `--uptodate`. |

### Slicing actions

| Flag | Use |
|---|---|
| `--slice <option>` | Run slicing. `0` means all plates; a positive number selects that plate. |
| `--no-check` | Skip validity checks. Use cautiously in automation. |
| `--allow-mix-temp` | Allow mixed high/low temperature filaments in one job. |
| `--skip-objects "3,5,10"` | Exclude objects by index. |
| `--mstpp <seconds>` | Maximum slicing time per plate. |
| `--mtcpp <count>` | Maximum triangle count per plate. |
| `--enable-timelapse` | Mark the job as timelapse-enabled. |
| `--normative-check` | Run normative checks. |

### Arrangement and transformations

| Flag | Use |
|---|---|
| `--arrange <option>` | Arrange behavior. `0` disables, `1` enables, other values behave as auto. |
| `--allow-rotations` | Allow object rotation during arrangement. |
| `--allow-multicolor-oneplate` | Allow multiple colors on one arranged plate. |
| `--avoid-extrusion-cali-region` | Avoid placing objects in the calibration region. |
| `--assemble` | Arrange supplied models and merge them into one model. |
| `--ensure-on-bed` | Lift objects onto the bed if they are partially below it. |
| `--orient <option>` | Orientation behavior. `0` disables, `1` enables, other values behave as auto. |
| `--rotate <degrees>` | Rotate around Z. |
| `--rotate-x <degrees>` | Rotate around X. |
| `--rotate-y <degrees>` | Rotate around Y. |
| `--scale <factor>` | Scale by a floating-point factor, for example `1.5`. |
| `--clone-objects "1,3,1"` | Clone objects from the load list. |
| `--repetitions <count>` | Repeat the whole model. |
| `--convert-unit` | Convert model units. |

### Output

| Flag | Use |
|---|---|
| `--export-3mf <file.3mf>` | Export the sliced project archive. For print jobs this is usually named `*.gcode.3mf`. |
| `--export-slicedata <directory>` | Write slicing cache data for later reuse. |
| `--export-settings <settings.json>` | Export the current settings. Useful for reproducibility. |
| `--export-stl` | Export objects as one merged STL. |
| `--export-stls` | Export objects as individual STL files. |
| `--outputdir <dir>` | Set output directory. |
| `--min-save` | Minimize output file size. Useful for repeated experiments. |

### Progress, logging, and inspection

| Flag | Use |
|---|---|
| `--pipe <pipename>` | Stream progress as newline-delimited JSON to a named pipe. |
| `--debug <level>` | Logging level: `0` fatal, `1` error, `2` warning, `3` info, `4` debug, `5` trace. |
| `--info` | Print model information without slicing. |
| `--help`, `-h` | Show CLI help. |

Progress pipe messages contain fields such as:

```json
{
  "plate_index": 0,
  "plate_count": 1,
  "plate_percent": 47.3,
  "total_percent": 47.3,
  "message": "Generating supports",
  "warning": null
}
```

### Metadata embedding

| Flag | Use |
|---|---|
| `--metadata-name "name1;name2"` | Metadata key list. Pair with `--metadata-value`. |
| `--metadata-value "value1;value2"` | Metadata values matching `--metadata-name`. |
| `--makerlab-name <name>` | Embed MakerLab name. |
| `--makerlab-version <version>` | Embed MakerLab version. |

### Downward compatibility checks

| Flag | Use |
|---|---|
| `--downward-check` | Check compatibility against machine settings. |
| `--downward-settings "machine1.json;machine2.json"` | Machine settings to check against. |

## Settings priority

Orca Slicer resolves settings in this order, from highest to lowest priority:

1. command-line flags;
2. settings loaded through `--load-settings` and `--load-filaments`;
3. settings embedded in the input 3MF.

That makes command-line overrides useful for optimization runs. For example, a generated 3MF can remain stable while the experiment changes slicing parameters:

```bash
orca-slicer \
  --slice 1 \
  --load-settings "profiles/machine.json;profiles/process.json" \
  --load-filaments "profiles/filament_pla.json" \
  --layer-height 0.12 \
  --sparse-infill-density 15% \
  --export-3mf runs/lh_012_infill_15/output.gcode.3mf \
  cad/out/fiddle.3mf
```

Any Orca setting key may be passable as a CLI flag. For safety, validate this against the exact Orca Slicer version in use. The Printago reference points to Orca Slicer's `src/libslic3r/PrintConfig.cpp` as the source of valid setting keys.

## Multi-part or multi-object slicing with assemble lists

When the CAD pipeline emits separate bodies, use `--load-assemble-list` rather than first hand-building a project file.

```json
{
  "plates": [
    {
      "plate_index": 1,
      "plate_name": "plate_1",
      "need_arrange": true,
      "objects": [
        {
          "path": "/tmp/fiddle_body.stl",
          "count": 1,
          "filaments": [1],
          "assemble_index": [1]
        },
        {
          "path": "/tmp/fiddle_label.stl",
          "count": 1,
          "filaments": [1],
          "assemble_index": [1]
        }
      ]
    }
  ]
}
```

```bash
orca-slicer \
  --slice 1 \
  --load-settings "profiles/machine.json;profiles/process.json" \
  --load-filaments "profiles/filament_pla.json" \
  --load-assemble-list runs/example/assemble-list.json \
  --export-3mf runs/example/output.gcode.3mf
```

Useful assemble-list fields:

| Field | Where | Notes |
|---|---|---|
| `plates` | top level | Array of plate definitions. |
| `plate_name` | plate | Required plate identifier. |
| `need_arrange` | plate | `true` lets Orca arrange objects; `false` expects explicit positions. |
| `objects` | plate | Required object list. |
| `plate_params` | plate | Optional plate-level setting overrides. |
| `path` | object | Absolute path to STL or 3MF geometry. |
| `count` | object | Number of copies. |
| `filaments` | object | 1-based filament slot indices. Length must be 1 or match `count`. |
| `assemble_index` | object | Objects sharing an index are merged into one composed model. |
| `pos_x`, `pos_y`, `pos_z` | object | Optional explicit positions or Z offsets. Useful when `need_arrange` is `false`. |
| `subtype` | object | Volume type. Default is `ModelPart`; other useful values include `NegativeVolume` and `ParameterModifier`. |
| `print_params` | object | Per-object setting overrides. |
| `height_ranges` | object | Height-range-specific overrides. |

## Reading progress from a named pipe

```bash
pipe="/tmp/orca-progress.pipe"
rm -f "$pipe"
mkfifo "$pipe"

cat "$pipe" | while IFS= read -r line; do
  printf 'orca progress: %s\n' "$line"
done &
reader_pid=$!

orca-slicer \
  --slice 1 \
  --load-settings "profiles/machine.json;profiles/process.json" \
  --load-filaments "profiles/filament_pla.json" \
  --pipe "$pipe" \
  --export-3mf runs/example/output.gcode.3mf \
  cad/out/fiddle.3mf

kill "$reader_pid" 2>/dev/null || true
rm -f "$pipe"
```

For a future wrapper in `slice/`, parse each line as JSON and persist progress updates into the run log.

## What is inside `*.gcode.3mf`

The output from `--export-3mf` is a ZIP-style 3MF archive. Useful files include:

```text
Metadata/
  plate_1.gcode
  plate_1.png
  slice_info.config
  project_settings.config
  model_settings.config
3D/
  3dmodel.model
```

Practical uses:

- `Metadata/plate_1.gcode`: raw G-code for analysis or printers that do not consume `.gcode.3mf` directly.
- `Metadata/slice_info.config`: filament use, estimated time, layer count, and related slice metadata.
- `Metadata/project_settings.config`: resolved settings after profile loading and CLI overrides.
- `Metadata/model_settings.config`: object placement and model metadata.

Example extraction:

```bash
mkdir -p runs/example/extracted
unzip -q runs/example/output.gcode.3mf -d runs/example/extracted
ls runs/example/extracted/Metadata
```

## Gotchas for this project

### Pin the slicer version

The CLI is not treated as a stable public API. Record the exact Orca Slicer version in each experiment run and keep a copy of `orca-slicer --help` output in CI or documentation when upgrading.

### Validate `printer_model`

The printer model embedded in a 3MF can conflict with the loaded machine profile. If a design is routed to a different printer model, patch or regenerate the 3MF metadata so the input and loaded machine settings agree.

### `.gcode.3mf` is not plain `.gcode`

Downstream tools must either accept `.gcode.3mf` or extract `Metadata/plate_N.gcode` first.

### Clean up working directories

A single slice can create hundreds of MB of temporary and output files. The wrapper should use a per-run sandbox and delete it in a `finally` block unless the run is explicitly marked for debugging.

### Headless thumbnails may be blank

The plate thumbnail inside the output archive may require OpenGL and may be blank in headless environments. Do not depend on it for experiment correctness.

## Suggested repository integration

Add an Orca wrapper alongside the existing slicing code:

```text
slice/
  orca.py              # Python wrapper around orca-slicer
  orca_profiles.py     # profile/path helpers
  extract_3mf.py       # output metadata and G-code extraction
profiles/
  machine/*.json
  process/*.json
  filament/*.json
```

Minimum wrapper behavior:

1. create an isolated working directory;
2. copy or generate input geometry into the working directory;
3. resolve machine, process, and filament profile paths;
4. build the Orca CLI argument list without shell interpolation;
5. optionally create a named pipe and stream progress into the run log;
6. run with a timeout;
7. store the exact command, Orca version, profile hashes, and output paths;
8. extract `slice_info.config`, `project_settings.config`, and raw G-code where needed;
9. delete temporary files unless debugging is enabled.

A first milestone can be simple: slice one generated 3MF with one PLA filament profile and export `output.gcode.3mf` plus extracted `slice_info.config`. After that, add optimization parameters as explicit CLI overrides.
