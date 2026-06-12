import cadquery as cq

def create_violin_body(length=355, lower_bout=208, upper_bout=168, c_bout=110, top_thickness=4, back_thickness=4, rib_thickness=4, top_arch_height=15, back_arch_height=15, rib_height=30, f_hole_length=70, f_hole_spacing=80, neck_length=130, neck_width=30, neck_height=20, bridge_width=40, bridge_height=30, bridge_thickness=5, soundpost_radius=3, soundpost_x_offset=15, soundpost_y_offset=-15, bass_bar_length=200, bass_bar_width=5, bass_bar_height=10, bass_bar_x_offset=-15, bass_bar_y_offset=0):
    """
    Generate a simplified parametric violin body.
    """
    pts = [
        (0, -length / 2.0),
        (lower_bout / 2.0, -length * 0.25),
        (c_bout / 2.0, 0),
        (upper_bout / 2.0, length * 0.25),
        (0, length / 2.0),
        (-upper_bout / 2.0, length * 0.25),
        (-c_bout / 2.0, 0),
        (-lower_bout / 2.0, -length * 0.25)
    ]

    # Helper to create an arched cylinder intersection
    def get_cylinders(arch_height, z_offset, mirror=False):
        r_x = ( (lower_bout/2)**2 + arch_height**2 ) / (2 * arch_height)
        cyl_x = cq.Workplane("XZ").center(0, -r_x + arch_height + z_offset).circle(r_x).extrude(length, both=True)
        r_y = ( (length/2)**2 + arch_height**2 ) / (2 * arch_height)
        cyl_y = cq.Workplane("YZ").center(0, -r_y + arch_height + z_offset).circle(r_y).extrude(lower_bout, both=True)
        if mirror:
            cyl_x = cyl_x.mirror("XY")
            cyl_y = cyl_y.mirror("XY")
        return cyl_x, cyl_y

    # Outer bounding domes
    out_top_cyl_x, out_top_cyl_y = get_cylinders(top_arch_height, rib_height)
    out_back_cyl_x, out_back_cyl_y = get_cylinders(back_arch_height, 0, mirror=True)

    # Total volume bounding box
    total_volume = cq.Workplane("XY").polyline(pts).close().extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    total_volume = total_volume.intersect(out_top_cyl_x).intersect(out_top_cyl_y).intersect(out_back_cyl_x).intersect(out_back_cyl_y)

    # Inner cavity domes
    in_top_cyl_x, in_top_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness)
    # Fix back cavity offset: moving it by -back_thickness before mirror means it ends up inside
    # Wait, get_cylinders uses mirror=True.
    # The outer dome starts at z_offset=0 and curves to -back_arch_height.
    # The inner dome should start at z_offset=back_thickness.
    # When mirrored, it starts at -back_thickness and curves to -back_arch_height - back_thickness.
    # But wait, we want the cavity to NOT reach the bottom. So the cavity should curve down to -back_arch_height + back_thickness.
    # So the inner back dome should have arch_height = back_arch_height?
    # If we use the same arch_height, translating by back_thickness (in the positive Z before mirroring, so -back_thickness after)
    # means it shifts downwards by back_thickness.
    # But we want the cavity to shift UPWARDS by back_thickness relative to the outer dome.
    # So before mirroring, we should shift DOWNWARDS by back_thickness (so z_offset = -back_thickness).
    # Then after mirror, it will be shifted UPWARDS by back_thickness!
    in_back_cyl_x, in_back_cyl_y = get_cylinders(back_arch_height, -back_thickness, mirror=True)

    # Cavity volume
    cavity_volume = cq.Workplane("XY").polyline(pts).close().offset2D(-rib_thickness).extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    cavity_volume = cavity_volume.intersect(in_top_cyl_x).intersect(in_top_cyl_y).intersect(in_back_cyl_x).intersect(in_back_cyl_y)

    body = total_volume.cut(cavity_volume)

    # Add F-holes
    f_hole_width = 8.0 # typical simplified f-hole width

    f_holes_tool = cq.Workplane("XY").pushPoints([
        (f_hole_spacing / 2.0, 0),
        (-f_hole_spacing / 2.0, 0)
    ]).slot2D(f_hole_length, f_hole_width, 90).extrude(1000).translate((0, 0, -500))

    # Cut f-holes only through the top part by intersecting the cutting tool with a box above rib_height/2
    f_holes_tool = f_holes_tool.intersect(cq.Workplane("XY").box(1000, 1000, 1000).translate((0, 0, 500 + rib_height/2)))
    body = body.cut(f_holes_tool)

    # Add Neck
    neck = cq.Workplane("XY").center(0, length / 2.0 + neck_length / 2.0).box(neck_width, neck_length, neck_height)
    neck = neck.translate((0, 0, rib_height - neck_height / 2.0))

    final_body = body.union(neck)

    # Add Bridge
    bridge = cq.Workplane("XY").box(bridge_width, bridge_thickness, bridge_height)
    bridge = bridge.translate((0, 0, rib_height + top_arch_height + bridge_height / 2.0))
    final_body = final_body.union(bridge)

    # Add Soundpost (spanning the cavity)
    soundpost = cq.Workplane("XY").center(soundpost_x_offset, soundpost_y_offset).circle(soundpost_radius).extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    soundpost = soundpost.intersect(cavity_volume)
    final_body = final_body.union(soundpost)

    # Add Bass Bar
    bb_top_cyl_x, bb_top_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness)
    bb_bottom_cyl_x, bb_bottom_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness - bass_bar_height)

    bass_bar_full = cq.Workplane("XY").center(bass_bar_x_offset, bass_bar_y_offset).rect(bass_bar_width, bass_bar_length).extrude(rib_height + top_arch_height).translate((0, 0, 0))
    bass_bar_full = bass_bar_full.intersect(bb_top_cyl_x).intersect(bb_top_cyl_y)
    bass_bar_full = bass_bar_full.cut(bb_bottom_cyl_x.intersect(bb_bottom_cyl_y))

    final_body = final_body.union(bass_bar_full)

    return final_body

import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate parametric violin body.")
    parser.add_argument("--length", type=float, default=355, help="Length of the body")
    parser.add_argument("--lower_bout", type=float, default=208, help="Width of the lower bout")
    parser.add_argument("--upper_bout", type=float, default=168, help="Width of the upper bout")
    parser.add_argument("--c_bout", type=float, default=110, help="Width of the c-bout")
    parser.add_argument("--top_thickness", type=float, default=4, help="Top plate thickness")
    parser.add_argument("--back_thickness", type=float, default=4, help="Back plate thickness")
    parser.add_argument("--rib_thickness", type=float, default=4, help="Rib thickness")
    parser.add_argument("--top_arch_height", type=float, default=15, help="Arch height of the top plate")
    parser.add_argument("--back_arch_height", type=float, default=15, help="Arch height of the back plate")
    parser.add_argument("--rib_height", type=float, default=30, help="Height of the ribs")
    parser.add_argument("--f_hole_length", type=float, default=70, help="Length of the F-holes")
    parser.add_argument("--f_hole_spacing", type=float, default=80, help="Spacing between the F-holes")
    parser.add_argument("--neck_length", type=float, default=130, help="Length of the neck")
    parser.add_argument("--neck_width", type=float, default=30, help="Width of the neck")
    parser.add_argument("--neck_height", type=float, default=20, help="Height/thickness of the neck")
    parser.add_argument("--bridge_width", type=float, default=40, help="Width of the bridge")
    parser.add_argument("--bridge_height", type=float, default=30, help="Height of the bridge")
    parser.add_argument("--bridge_thickness", type=float, default=5, help="Thickness of the bridge")
    parser.add_argument("--soundpost_radius", type=float, default=3, help="Radius of the soundpost")
    parser.add_argument("--soundpost_x_offset", type=float, default=15, help="X offset of the soundpost")
    parser.add_argument("--soundpost_y_offset", type=float, default=-15, help="Y offset of the soundpost")
    parser.add_argument("--bass_bar_length", type=float, default=200, help="Length of the bass bar")
    parser.add_argument("--bass_bar_width", type=float, default=5, help="Width of the bass bar")
    parser.add_argument("--bass_bar_height", type=float, default=10, help="Height of the bass bar")
    parser.add_argument("--bass_bar_x_offset", type=float, default=-15, help="X offset of the bass bar")
    parser.add_argument("--bass_bar_y_offset", type=float, default=0, help="Y offset of the bass bar")
    args = parser.parse_args()

    params = {
        "length": args.length,
        "lower_bout": args.lower_bout,
        "upper_bout": args.upper_bout,
        "c_bout": args.c_bout,
        "top_thickness": args.top_thickness,
        "back_thickness": args.back_thickness,
        "rib_thickness": args.rib_thickness,
        "top_arch_height": args.top_arch_height,
        "back_arch_height": args.back_arch_height,
        "rib_height": args.rib_height,
        "f_hole_length": args.f_hole_length,
        "f_hole_spacing": args.f_hole_spacing,
        "neck_length": args.neck_length,
        "neck_width": args.neck_width,
        "neck_height": args.neck_height,
        "bridge_width": args.bridge_width,
        "bridge_height": args.bridge_height,
        "bridge_thickness": args.bridge_thickness,
        "soundpost_radius": args.soundpost_radius,
        "soundpost_x_offset": args.soundpost_x_offset,
        "soundpost_y_offset": args.soundpost_y_offset,
        "bass_bar_length": args.bass_bar_length,
        "bass_bar_width": args.bass_bar_width,
        "bass_bar_height": args.bass_bar_height,
        "bass_bar_x_offset": args.bass_bar_x_offset,
        "bass_bar_y_offset": args.bass_bar_y_offset
    }

    violin = create_violin_body(**params)

    # Export to step
    cq.exporters.export(violin, "violin_body.step")

    # Export parameters to JSON
    with open("violin_body.json", "w") as f:
        json.dump(params, f, indent=4)
