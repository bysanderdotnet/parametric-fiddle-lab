"""Single source of truth for violin geometry parameters.

Drives cad/violin.py (argparse) and opt/optimize.py (Optuna search space +
cad CLI arg construction). Default values live once in
cad.violin.create_violin_body's signature; this spec owns the param names,
kinds, search ranges, and help text.

SPEC entry = (name, kind, opt, help)
  kind: "float" | "str" | "bool"
  opt:  (low, high) for float; [choices] for str/bool; None = not optimized
"""

SPEC = [
    ("length", "float", (340.0, 370.0), "Length of the body"),
    ("lower_bout", "float", (200.0, 220.0), "Width of the lower bout"),
    ("upper_bout", "float", (160.0, 180.0), "Width of the upper bout"),
    ("c_bout", "float", (100.0, 120.0), "Width of the c-bout"),
    ("top_thickness", "float", (2.0, 6.0), "Top plate thickness"),
    ("back_thickness", "float", (2.0, 6.0), "Back plate thickness"),
    ("rib_thickness", "float", (2.0, 6.0), "Rib thickness"),
    ("top_arch_height", "float", (10.0, 25.0), "Arch height of the top plate"),
    ("back_arch_height", "float", (10.0, 25.0), "Arch height of the back plate"),
    ("rib_height", "float", (25.0, 40.0), "Height of the ribs"),
    ("f_hole_length", "float", (60.0, 90.0), "Length of the F-holes"),
    ("f_hole_spacing", "float", (60.0, 100.0), "Spacing between the F-holes"),
    ("f_hole_width", "float", (5.0, 12.0), "Width of the F-holes"),
    ("f_hole_thickness", "float", (1.0, 5.0), "Thickness of the f-hole edge reinforcement"),
    ("f_hole_profile", "str", ["slot", "classic"], "Profile of the F-holes (slot or classic)"),
    ("f_hole_top_radius", "float", (3.0, 6.0), "Top radius of classic F-holes"),
    ("f_hole_bottom_radius", "float", (3.0, 6.0), "Bottom radius of classic F-holes"),
    ("f_hole_x_offset", "float", (-20.0, 20.0), "X offset of the F-holes"),
    ("f_hole_y_offset", "float", (-20.0, 20.0), "Y offset of the F-holes"),
    ("f_hole_angle", "float", (75.0, 105.0), "Angle of the F-holes"),
    ("neck_length", "float", (110.0, 150.0), "Length of the neck"),
    ("neck_width_top", "float", (20.0, 30.0), "Width of the neck at the nut"),
    ("neck_width_bottom", "float", (30.0, 40.0), "Width of the neck at the body"),
    ("neck_thickness", "float", (15.0, 30.0), "Height/thickness of the neck"),
    ("neck_angle", "float", (2.0, 8.0), "Angle of the neck assembly relative to the body"),
    ("bridge_width_bottom", "float", (35.0, 45.0), "Width of the bridge at the bottom"),
    ("bridge_width_top", "float", (25.0, 35.0), "Width of the bridge at the top"),
    ("bridge_height", "float", (20.0, 40.0), "Height of the bridge"),
    ("bridge_thickness", "float", (3.0, 8.0), "Thickness of the bridge"),
    ("bridge_radius", "float", (15.0, 40.0), "Radius of the bridge top curvature"),
    ("bridge_inner_curve_radius", "float", (5.0, 15.0), "Radius of the inner curve on the bridge sides"),
    ("bridge_side_cutout_radius", "float", (3.0, 10.0), "Radius of the side cutouts on the bridge"),
    ("bridge_cutout_radius", "float", (2.0, 8.0), "Radius of the bridge cutouts"),
    ("bridge_cutout_y_offset", "float", (5.0, 20.0), "Vertical offset of the bridge cutouts"),
    ("bridge_central_cutout", "bool", [True, False], "Whether to include the central bridge cutout"),
    ("bridge_central_cutout_radius", "float", (2.0, 8.0), "Radius of the central bridge cutout"),
    ("bridge_central_cutout_y_offset", "float", (10.0, 25.0), "Vertical offset of the central bridge cutout"),
    ("bridge_foot_length", "float", (5.0, 15.0), "Length of the bridge feet"),
    ("bridge_foot_width", "float", (3.0, 10.0), "Width (thickness) of the bridge feet"),
    ("bridge_foot_height", "float", (2.0, 10.0), "Height of the bridge feet cutout"),
    ("bridge_cutouts", "bool", [True, False], "Whether to include bridge cutouts"),
    ("bridge_y_offset", "float", (-20.0, 20.0), "Y offset of the bridge"),
    ("soundpost_radius", "float", (2.0, 5.0), "Radius of the soundpost"),
    ("soundpost_x_offset", "float", (5.0, 25.0), "X offset of the soundpost"),
    ("soundpost_y_offset", "float", (-25.0, -5.0), "Y offset of the soundpost"),
    ("bass_bar_length", "float", (150.0, 250.0), "Length of the bass bar"),
    ("bass_bar_width", "float", (3.0, 8.0), "Width of the bass bar"),
    ("bass_bar_height", "float", (5.0, 15.0), "Height of the bass bar"),
    ("bass_bar_x_offset", "float", (-25.0, -5.0), "X offset of the bass bar"),
    ("bass_bar_y_offset", "float", (-20.0, 20.0), "Y offset of the bass bar"),
    ("bass_bar_angle", "float", (-15.0, 15.0), "Angle of the bass bar"),
    ("tailpiece_length", "float", (100.0, 120.0), "Length of the tailpiece"),
    ("tailpiece_width_top", "float", (30.0, 45.0), "Width of the tailpiece near bridge"),
    ("tailpiece_width_bottom", "float", (15.0, 25.0), "Width of the tailpiece near saddle"),
    ("tailpiece_thickness", "float", (3.0, 8.0), "Thickness of the tailpiece"),
    ("tailpiece_y_offset", "float", (-20.0, 20.0), "Y offset of the tailpiece"),
    ("purfling_groove_depth", "float", (0.5, 2.0), "Depth of the purfling groove"),
    ("purfling_groove_width", "float", (0.5, 2.0), "Width of the purfling groove"),
    ("purfling_groove_offset", "float", (1.0, 4.0), "Offset of the purfling groove from the edge"),
    ("fingerboard_length", "float", (250.0, 290.0), "Length of the fingerboard"),
    ("fingerboard_width_top", "float", (22.0, 26.0), "Width of the fingerboard near the nut"),
    ("fingerboard_width_bottom", "float", (40.0, 44.0), "Width of the fingerboard near the bridge"),
    ("fingerboard_thickness", "float", (4.0, 7.0), "Thickness of the fingerboard"),
    ("fingerboard_radius", "float", (30.0, 60.0), "Radius of the fingerboard curvature"),
    ("fingerboard_end_shape", "str", ["flat", "curve"], "Shape of the fingerboard end near the bridge"),
    ("pegbox_length", "float", (65.0, 75.0), "Length of the pegbox"),
    ("pegbox_width", "float", (22.0, 26.0), "Width of the pegbox"),
    ("pegbox_depth", "float", (18.0, 22.0), "Depth of the pegbox"),
    ("pegbox_thickness", "float", (4.0, 6.0), "Wall thickness of the pegbox"),
    ("pegbox_angle", "float", (0.0, 15.0), "Angle of the pegbox relative to the neck"),
    ("peg_hole_radius", "float", (2.5, 3.5), "Radius of the peg holes"),
    ("peg_spacing", "float", (14.0, 16.0), "Spacing between pegs"),
    ("peg_length", "float", (35.0, 55.0), "Length of the pegs"),
    ("peg_width", "float", (15.0, 25.0), "Width of the peg head"),
    ("peg_head_thickness", "float", (3.0, 10.0), "Thickness of the peg head"),
    ("endpin_length", "float", (15.0, 25.0), "Length of the endpin"),
    ("endpin_radius", "float", (3.0, 6.0), "Radius of the endpin"),
    ("nut_length", "float", (3.0, 8.0), "Length of the nut"),
    ("nut_width", "float", (22.0, 26.0), "Width of the nut"),
    ("nut_height", "float", (5.0, 10.0), "Height of the nut"),
    ("saddle_length", "float", (3.0, 8.0), "Length of the saddle"),
    ("saddle_width", "float", (25.0, 35.0), "Width of the saddle"),
    ("saddle_height", "float", (4.0, 8.0), "Height of the saddle"),
    ("scroll_radius", "float", (8.0, 12.0), "Radius of the scroll"),
    ("scroll_width", "float", (18.0, 22.0), "Width of the scroll"),
    ("chinrest_x_offset", "float", (-60.0, -20.0), "X offset of the chinrest"),
    ("chinrest_y_offset", "float", (-160.0, -120.0), "Y offset of the chinrest"),
    ("chinrest_width", "float", (60.0, 100.0), "Width of the chinrest"),
    ("chinrest_length", "float", (40.0, 70.0), "Length of the chinrest"),
    ("chinrest_height", "float", (10.0, 25.0), "Height of the chinrest"),
    ("fine_tuner_radius", "float", (1.0, 4.0), "Radius of the fine tuners"),
    ("fine_tuner_height", "float", (4.0, 15.0), "Height of the fine tuners"),
    ("chinrest_cutout_radius", "float", (40.0, 80.0), "Radius of the chinrest cutout sphere"),
    ("chinrest_cutout_depth", "float", (2.0, 10.0), "Depth of the chinrest cutout"),
    ("c_bout_cutout_radius", "float", (30.0, 60.0), "Radius of the C-bout cutout"),
    ("top_block_width", "float", (30.0, 60.0), "Width of the top block"),
    ("top_block_length", "float", (10.0, 30.0), "Length of the top block"),
    ("bottom_block_width", "float", (30.0, 60.0), "Width of the bottom block"),
    ("bottom_block_length", "float", (10.0, 30.0), "Length of the bottom block"),
    ("corner_block_width", "float", (10.0, 30.0), "Width of the corner blocks"),
    ("corner_block_length", "float", (10.0, 30.0), "Length of the corner blocks"),
]

NAMES = [name for name, _, _, _ in SPEC]


def add_arguments(parser, defaults):
    """Register one argparse argument per SPEC entry, default pulled from `defaults`."""
    import argparse
    for name, kind, _opt, help_ in SPEC:
        if kind == "bool":
            parser.add_argument(f"--{name}", action=argparse.BooleanOptionalAction,
                                default=defaults[name], help=help_)
        else:
            parser.add_argument(f"--{name}", type=(float if kind == "float" else str),
                                default=defaults[name], help=help_)


def suggest(trial):
    """Build a {name: value} dict from an Optuna trial over the optimized params."""
    vals = {}
    for name, kind, opt, _ in SPEC:
        if opt is None:
            continue
        if kind == "float":
            vals[name] = trial.suggest_float(name, opt[0], opt[1])
        else:  # str/bool categorical
            vals[name] = trial.suggest_categorical(name, opt)
    return vals


def cli_args(values):
    """Turn a {name: value} dict into cad/violin.py CLI args (SPEC order)."""
    args = []
    kinds = {name: kind for name, kind, _, _ in SPEC}
    for name in NAMES:
        if name not in values:
            continue
        if kinds[name] == "bool":
            args.append(f"--{name}" if values[name] else f"--no-{name}")
        else:
            args += [f"--{name}", str(values[name])]
    return args
