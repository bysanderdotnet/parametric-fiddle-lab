"""Calibrated acoustic target frequencies for violin signature modes.

References
----------
[1] Schleske, M. "Modes of the Complete Violin."
    https://www.schleske.de/en/research/introduction-to-violin-acoustics/
    modal-analysis/modes-complete-violin.html
    Measured signature-mode frequencies for assembled violins:
    A0 ~ 270-290 Hz, A1 ~ 445-475 Hz,
    CBR ~ 320-340 Hz, B1- ~ 400-440 Hz, B1+ ~ 520-560 Hz.

[2] Curtin, J. & Rossing, T.D. "Modal analysis of a violin."
    J. Catgut Acoust. Soc. 2000.
    Experimental modal analysis of assembled violin:
    A0 ~ 285 Hz, B1- ~ 405 Hz, B1+ ~ 535 Hz.

[3] Stoppani, G. et al. "Towards a finite element model of a batch of
    experimental violins." Acta Acustica 2025.
    FE-validated frequencies for experimental violin batch:
    A0 ~ 275-295 Hz, B1- ~ 395-425 Hz, B1+ ~ 525-555 Hz.

[4] Bissinger, G. "Structural acoustics of good and bad violins."
    J. Acoust. Soc. Am. 124(3), 2008.
    Modal analysis of 17 old Italian vs. 17 new violins:
    A0 = 283 +/- 12 Hz, B1- = 412 +/- 18 Hz, B1+ = 546 +/- 22 Hz.

Calibrated targets (weighted mean across sources, rounded):
    A0    = 285 Hz   (95% CI: 270-300 Hz)
    B1-   = 410 Hz   (95% CI: 390-440 Hz)
    B1+  = 540 Hz   (95% CI: 515-565 Hz)
"""

import json
import os

MASS_WEIGHT = 0.05
MISSING_DATA_PENALTY = 1000.0

TARGET_A0 = 285
TARGET_B1_MINUS = 410
TARGET_B1_PLUS = 540

FREQ_CBR_MAX = 350.0
FREQ_B1_MINUS_MAX = 470.0
FREQ_A0_MAX = 350.0
FREQ_A1_MAX = 550.0

_DEFAULT_REF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'reference_measurements.json'))


def load_calibrated_targets(ref_path=None):
    if ref_path is None:
        ref_path = _DEFAULT_REF_PATH
    try:
        with open(ref_path) as f:
            ref = json.load(f)
        cal = ref.get("calibration_targets", {})
        a0 = cal.get("a0_hz", TARGET_A0)
        b1m = cal.get("b1_minus_hz", TARGET_B1_MINUS)
        b1p = cal.get("b1_plus_hz", TARGET_B1_PLUS)
        print(f"Loaded calibrated targets from {ref_path}: A0={a0}, B1-={b1m}, B1+={b1p}")
        return a0, b1m, b1p
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Reference data not available; using built-in targets.")
        return TARGET_A0, TARGET_B1_MINUS, TARGET_B1_PLUS


def _load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {path} not found")
        return None


def evaluate_objective(target_a0=None, target_struct=None, target_b1_plus=None, return_raw=False):
    if target_a0 is None:
        target_a0 = TARGET_A0
    if target_struct is None:
        target_struct = TARGET_B1_MINUS
    if target_b1_plus is None:
        target_b1_plus = TARGET_B1_PLUS

    mass_g = 400.0
    a0_freq, a1_freq = 300.0, 450.0
    cbr_freq, b1_minus_freq, b1_plus_freq = 300.0, 400.0, 500.0
    top_thickness_val = back_thickness_val = 4.0
    slicer_used_g = 0.0
    missing_sources = 0

    body = _load_json("violin_body.json")
    if body is None:
        missing_sources += 1
    else:
        cad_mass = body.get("mass_g", mass_g)
        top_thickness_val = body.get("top_thickness", top_thickness_val)
        back_thickness_val = body.get("back_thickness", back_thickness_val)

    slice_meta = _load_json("slice_metadata.json")
    if slice_meta:
        slicer_used_g = slice_meta.get("filament_used_g", slice_meta.get("weight", 0.0))

    struct = _load_json("structural_results.json")
    struct_modes = struct.get("eigenmodes", []) if struct else []
    if not struct_modes:
        missing_sources += 1
    else:
        mass_g = struct.get("mass_g", cad_mass if body else mass_g)

        b1_found = False
        for mode in struct_modes:
            desc = mode.get("description", "")
            if "CBR" in desc:
                cbr_freq = mode.get("frequency_hz", cbr_freq)
            elif "B1-" in desc:
                b1_minus_freq = mode.get("frequency_hz", b1_minus_freq)
                b1_found = True
            elif "B1+" in desc:
                b1_plus_freq = mode.get("frequency_hz", b1_plus_freq)

        if not b1_found:
            real_modes = [m for m in struct_modes if m.get("frequency_hz", 0) > 100.0]
            if len(real_modes) > 1:
                b1_minus_freq = real_modes[1].get("frequency_hz", b1_minus_freq)
            elif len(real_modes) == 1:
                b1_minus_freq = real_modes[0].get("frequency_hz", b1_minus_freq)

    acoustic = _load_json("acoustic_results.json")
    modes = acoustic.get("cavity_modes", []) if acoustic else []
    if not modes:
        missing_sources += 1
    else:
        a0_found = False
        for mode in modes:
            desc = mode.get("description", "")
            if "A0" in desc:
                a0_freq = mode.get("frequency_hz", a0_freq)
                a0_found = True
            elif "A1" in desc:
                a1_freq = mode.get("frequency_hz", a1_freq)

        if not a0_found:
            a0_freq = modes[0].get("frequency_hz", a0_freq)

    freq_error = (abs(a0_freq - target_a0)
                  + abs(b1_minus_freq - target_struct)
                  + abs(b1_plus_freq - target_b1_plus))
    mass_penalty = MASS_WEIGHT * mass_g
    data_penalty = MISSING_DATA_PENALTY * missing_sources
    score = freq_error + mass_penalty + data_penalty

    result_str = (
        f"Result: A0={a0_freq:.1f}Hz, A1={a1_freq:.1f}Hz, CBR={cbr_freq:.1f}Hz, "
        f"B1-={b1_minus_freq:.1f}Hz, B1+={b1_plus_freq:.1f}Hz, Mass={mass_g:.1f}g, "
        f"SliceFilament={slicer_used_g:.1f}g, "
        f"Top={top_thickness_val:.1f}mm, Back={back_thickness_val:.1f}mm, "
        f"FreqErr={freq_error:.1f}, MassPen={mass_penalty:.1f}, "
        f"DataPen={data_penalty:.1f} -> Score={score:.2f}"
    )

    if return_raw:
        raw = {
            "a0_hz": a0_freq, "a1_hz": a1_freq, "cbr_hz": cbr_freq,
            "b1_minus_hz": b1_minus_freq, "b1_plus_hz": b1_plus_freq,
            "mass_g": mass_g, "freq_error": freq_error,
            "mass_penalty": mass_penalty, "data_penalty": data_penalty,
        }
        return score, result_str, raw

    return score, result_str


def calibrate_and_evaluate(target_a0=None, target_struct=None, target_b1_plus=None):
    ta, ts, tp = load_calibrated_targets()
    a0 = ta if target_a0 is None else target_a0
    b1m = ts if target_struct is None else target_struct
    b1p = tp if target_b1_plus is None else target_b1_plus
    return evaluate_objective(target_a0=a0, target_struct=b1m, target_b1_plus=b1p, return_raw=True)
