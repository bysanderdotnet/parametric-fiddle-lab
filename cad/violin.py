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

if __name__ == "__main__":
    violin = create_violin_body()
    # Export to step
    cq.exporters.export(violin, "violin_body.step")
