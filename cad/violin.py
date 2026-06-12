import cadquery as cq

def create_violin_body(length=355, lower_bout=208, upper_bout=168, c_bout=110, thickness=4, f_hole_length=70, f_hole_spacing=80, neck_length=130, neck_width=30, neck_height=20, bridge_width=40, bridge_height=30, bridge_thickness=5, soundpost_radius=3, soundpost_x_offset=15, soundpost_y_offset=-15):
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

    body = cq.Workplane("XY").polyline(pts).close().extrude(30)

    # Hollow it out
    hollowed_body = body.faces("<Z").shell(thickness)

    # Add F-holes
    f_hole_width = 8.0 # typical simplified f-hole width

    with_f_holes = hollowed_body.faces(">Z").workplane().pushPoints([
        (f_hole_spacing / 2.0, 0),
        (-f_hole_spacing / 2.0, 0)
    ]).slot2D(f_hole_length, f_hole_width, 90).cutBlind(-thickness * 2)

    # Add Neck
    neck = cq.Workplane("XY").center(0, length / 2.0 + neck_length / 2.0).box(neck_width, neck_length, neck_height)
    # Move the neck slightly up in Z to align with the body top, or just union it at z=0
    # since body extrudes 30 up from Z=0. We'll elevate it so its top aligns with the violin's top (Z=30).
    neck = neck.translate((0, 0, 30 - neck_height / 2.0))

    final_body = with_f_holes.union(neck)

    # Add Bridge
    bridge = cq.Workplane("XY").box(bridge_width, bridge_thickness, bridge_height)
    # Move the bridge slightly up in Z to align with the body top.
    bridge = bridge.translate((0, 0, 30 + bridge_height / 2.0))
    final_body = final_body.union(bridge)

    # Add Soundpost
    soundpost_height = 30 - 2 * thickness
    soundpost = cq.Workplane("XY").cylinder(soundpost_height, soundpost_radius)
    soundpost = soundpost.translate((soundpost_x_offset, soundpost_y_offset, 15))
    final_body = final_body.union(soundpost)

    return final_body

import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate parametric violin body.")
    parser.add_argument("--length", type=float, default=355, help="Length of the body")
    parser.add_argument("--lower_bout", type=float, default=208, help="Width of the lower bout")
    parser.add_argument("--upper_bout", type=float, default=168, help="Width of the upper bout")
    parser.add_argument("--c_bout", type=float, default=110, help="Width of the c-bout")
    parser.add_argument("--thickness", type=float, default=4, help="Wall thickness")
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
    args = parser.parse_args()

    params = {
        "length": args.length,
        "lower_bout": args.lower_bout,
        "upper_bout": args.upper_bout,
        "c_bout": args.c_bout,
        "thickness": args.thickness,
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
        "soundpost_y_offset": args.soundpost_y_offset
    }

    violin = create_violin_body(**params)

    # Export to step
    cq.exporters.export(violin, "violin_body.step")

    # Export parameters to JSON
    with open("violin_body.json", "w") as f:
        json.dump(params, f, indent=4)
