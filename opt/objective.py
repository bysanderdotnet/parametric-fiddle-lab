import json

# Objective weights (single source of truth; tunable).
#
# Acoustic/structural frequency matching is the primary design goal, so those
# error terms dominate the score. Mass is a mild secondary regularizer that
# only breaks ties toward lighter/cheaper prints — it is NOT 20 separate
# per-part penalties (the old formula summed ~20 component masses at x5.0 each,
# which dwarfed the frequency terms and biased the optimizer into shrinking
# every part regardless of acoustics, while also double-counting mass via
# separate mass/volume/thickness terms).
#
# Missing or empty simulation output is penalized explicitly so a failed trial
# cannot masquerade as a good score by falling back to rosy default frequencies.
MASS_WEIGHT = 0.05             # score per gram of body mass
MISSING_DATA_PENALTY = 1000.0  # score per absent/empty simulation result source


def _load_json(path):
    """Return parsed JSON dict, or None if the file is missing."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {path} not found")
        return None


def evaluate_objective(target_a0=290.0, target_struct=400.0, target_b1_plus=540.0):
    # Neutral defaults; only used to keep the report readable. Genuine missing
    # data is charged MISSING_DATA_PENALTY rather than silently scored as good.
    mass_g = 400.0
    a0_freq, a1_freq = 300.0, 450.0
    cbr_freq, b1_minus_freq, b1_plus_freq = 300.0, 400.0, 500.0
    top_thickness_val = back_thickness_val = 4.0
    missing_sources = 0

    body = _load_json("violin_body.json")
    if body is None:
        missing_sources += 1
    else:
        mass_g = body.get("mass_g", mass_g)
        top_thickness_val = body.get("top_thickness", top_thickness_val)
        back_thickness_val = body.get("back_thickness", back_thickness_val)

    struct = _load_json("structural_results.json")
    struct_modes = struct.get("eigenmodes", []) if struct else []
    if not struct_modes:
        missing_sources += 1
    else:
        mass_g = struct.get("mass_g", mass_g)  # structural sim may refine mass

        # Find CBR, B1-, and B1+ modes explicitly by description.
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

        # Fallback if no B1- description: use the 2nd mode > 100Hz.
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
        # Find A0 and A1 modes explicitly by description.
        a0_found = False
        for mode in modes:
            desc = mode.get("description", "")
            if "A0" in desc:
                a0_freq = mode.get("frequency_hz", a0_freq)
                a0_found = True
            elif "A1" in desc:
                a1_freq = mode.get("frequency_hz", a1_freq)

        # Fallback to the first cavity mode if no A0 description is found.
        if not a0_found:
            a0_freq = modes[0].get("frequency_hz", a0_freq)

    # Score: frequency target matching dominates; mass is a mild regularizer;
    # missing/empty simulation output is penalized so failures don't score well.
    freq_error = (abs(a0_freq - target_a0)
                  + abs(b1_minus_freq - target_struct)
                  + abs(b1_plus_freq - target_b1_plus))
    mass_penalty = MASS_WEIGHT * mass_g
    data_penalty = MISSING_DATA_PENALTY * missing_sources
    score = freq_error + mass_penalty + data_penalty

    result_str = (
        f"Result: A0={a0_freq:.1f}Hz, A1={a1_freq:.1f}Hz, CBR={cbr_freq:.1f}Hz, "
        f"B1-={b1_minus_freq:.1f}Hz, B1+={b1_plus_freq:.1f}Hz, Mass={mass_g:.1f}g, "
        f"Top={top_thickness_val:.1f}mm, Back={back_thickness_val:.1f}mm, "
        f"FreqErr={freq_error:.1f}, MassPen={mass_penalty:.1f}, "
        f"DataPen={data_penalty:.1f} -> Score={score:.2f}"
    )

    return score, result_str
