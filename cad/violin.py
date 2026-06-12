import cadquery as cq

def create_violin_body(length=355, lower_bout=208, upper_bout=168, c_bout=110, thickness=4, f_hole_length=70, f_hole_spacing=80):
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

    return with_f_holes

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
    args = parser.parse_args()

    params = {
        "length": args.length,
        "lower_bout": args.lower_bout,
        "upper_bout": args.upper_bout,
        "c_bout": args.c_bout,
        "thickness": args.thickness,
        "f_hole_length": args.f_hole_length,
        "f_hole_spacing": args.f_hole_spacing
    }

    violin = create_violin_body(**params)

    # Export to step
    cq.exporters.export(violin, "violin_body.step")

    # Export parameters to JSON
    with open("violin_body.json", "w") as f:
        json.dump(params, f, indent=4)
