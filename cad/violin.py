import cadquery as cq

def create_violin_body(length=355, lower_bout=208, upper_bout=168, c_bout=110, thickness=4):
    """
    Generate a simplified parametric violin body.
    """
    # Create a simple generic body shape (not a real violin curve yet)
    # This is a very simplified placeholder.

    # Let us just create a box for now as a placeholder for the actual complex loft
    body = cq.Workplane("XY").box(lower_bout, length, 30)

    # Hollow it out
    hollowed_body = body.faces("<Z").shell(thickness)

    return hollowed_body

import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate parametric violin body.")
    parser.add_argument("--length", type=float, default=355, help="Length of the body")
    parser.add_argument("--lower_bout", type=float, default=208, help="Width of the lower bout")
    parser.add_argument("--upper_bout", type=float, default=168, help="Width of the upper bout")
    parser.add_argument("--c_bout", type=float, default=110, help="Width of the c-bout")
    parser.add_argument("--thickness", type=float, default=4, help="Wall thickness")
    args = parser.parse_args()

    params = {
        "length": args.length,
        "lower_bout": args.lower_bout,
        "upper_bout": args.upper_bout,
        "c_bout": args.c_bout,
        "thickness": args.thickness
    }

    violin = create_violin_body(**params)

    # Export to step
    cq.exporters.export(violin, "violin_body.step")

    # Export parameters to JSON
    with open("violin_body.json", "w") as f:
        json.dump(params, f, indent=4)
