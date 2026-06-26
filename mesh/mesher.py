import gmsh
import math
import os


def _tet_volume(p):
    """Signed volume of a tetrahedron defined by 4 points (4x3 array)."""
    return abs((
        (p[1][0] - p[0][0]) *
        ((p[2][1] - p[0][1]) * (p[3][2] - p[0][2]) -
         (p[2][2] - p[0][2]) * (p[3][1] - p[0][1])) +
        (p[1][1] - p[0][1]) *
        ((p[2][2] - p[0][2]) * (p[3][0] - p[0][0]) -
         (p[2][0] - p[0][0]) * (p[3][2] - p[0][2])) +
        (p[1][2] - p[0][2]) *
        ((p[2][0] - p[0][0]) * (p[3][1] - p[0][1]) -
         (p[2][1] - p[0][1]) * (p[3][0] - p[0][0]))
    ) / 6.0)


def compute_mesh_quality():
    """Print mesh quality statistics from the current model."""
    try:
        _, element_types, _ = gmsh.model.mesh.getElements(dim=3)
        if not element_types:
            return

        volumes = []
        for etype in element_types:
            _, _, node_tags = gmsh.model.mesh.getElementsByType(etype)
            if len(node_tags) == 0:
                continue
            for i in range(0, len(node_tags), 4):
                tet_nodes = list(node_tags[i:i + 4])
                coords = [gmsh.model.mesh.getNode(n)[0] for n in tet_nodes]
                vol = _tet_volume([c[:3] for c in coords])
                if vol > 0:
                    volumes.append(vol)

        if volumes:
            v = sorted(volumes)
            n = len(v)
            print(f"  Element count: {n}")
            print(f"  Volume range:  {v[0]:.2e} – {v[-1]:.2e} mm^3")
            print(f"  Mean volume:   {sum(v) / n:.2e} mm^3")
            ratio = v[-1] / v[0] if v[0] > 0 else float('inf')
            print(f"  Max/min ratio: {ratio:.1f}")
    except Exception as e:
        print(f"  (quality report skipped: {e})")


def generate_mesh(step_file, output_mesh, mesh_size=5.0, refine_f_holes=True):
    """
    Generate a 3D mesh from a STEP file using Gmsh with local refinement.

    Parameters
    ----------
    step_file : str
        Path to input STEP geometry.
    output_mesh : str
        Path for the output .msh file.
    mesh_size : float
        Base (coarse) mesh size in mm for bulk regions.
    refine_f_holes : bool
        If True, apply additional refinement near f-hole-like features by
        identifying small surface features from the CAD.
    """
    if not os.path.exists(step_file):
        raise FileNotFoundError(f"Input file not found: {step_file}")

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthFromPoints", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 1)

    try:
        gmsh.model.occ.importShapes(step_file)
        gmsh.model.occ.synchronize()

        plate_thickness = 4.0
        face_min_size = plate_thickness / 3.0
        fine_size = 0.7

        dim_tags = gmsh.model.getEntities(dim=2)
        surface_tags = [dt[1] for dt in dim_tags]

        if not surface_tags:
            # No 2D entities — fall back to uniform sizing.
            min_allowed = mesh_size * 0.5
            gmsh.model.mesh.field.add("MathEval", 1)
            gmsh.model.mesh.field.setString(1, "F", str(mesh_size))
            gmsh.model.mesh.field.setAsBackgroundMesh(1)
        else:
            # —— Field 1: Distance to ALL surfaces ——
            gmsh.model.mesh.field.add("Distance", 1)
            gmsh.model.mesh.field.setNumbers(1, "SurfacesList", surface_tags)
            gmsh.model.mesh.field.setNumber(1, "Sampling", 100)

            # —— Field 2: Threshold from all surfaces ——
            gmsh.model.mesh.field.add("Threshold", 2)
            gmsh.model.mesh.field.setNumber(2, "InField", 1)
            gmsh.model.mesh.field.setNumber(2, "SizeMin", face_min_size)
            gmsh.model.mesh.field.setNumber(2, "SizeMax", mesh_size)
            gmsh.model.mesh.field.setNumber(2, "DistMin", plate_thickness * 0.5)
            gmsh.model.mesh.field.setNumber(2, "DistMax", plate_thickness * 3.0)

            # —— Field 3: MathEval surface-taper blend ——
            gmsh.model.mesh.field.add("MathEval", 3)
            gmsh.model.mesh.field.setString(3, "F",
                f"F2 + ({mesh_size} - F2) * tanh(5 * F1 / {plate_thickness})")

            # —— Field 4–6: Very-fine zone near small features (f-holes) ——
            if refine_f_holes:
                areas = []
                for tag in surface_tags:
                    try:
                        xmin, ymin, zmin, xmax, ymax, zmax = \
                            gmsh.model.occ.getBoundingBox(2, tag)
                        diag = math.sqrt(
                            (xmax - xmin)**2 + (ymax - ymin)**2 + (zmax - zmin)**2
                        )
                        areas.append((diag, tag))
                    except Exception:
                        continue

                areas.sort()
                num_small = max(1, len(areas) // 8)
                small_tags = [t for _, t in areas[:num_small]]

                if small_tags:
                    gmsh.model.mesh.field.add("Distance", 4)
                    gmsh.model.mesh.field.setNumbers(4, "SurfacesList", small_tags)
                    gmsh.model.mesh.field.setNumber(4, "Sampling", 200)

                    gmsh.model.mesh.field.add("Threshold", 5)
                    gmsh.model.mesh.field.setNumber(5, "InField", 4)
                    gmsh.model.mesh.field.setNumber(5, "SizeMin", fine_size)
                    gmsh.model.mesh.field.setNumber(5, "SizeMax", face_min_size)
                    gmsh.model.mesh.field.setNumber(5, "DistMin", 1.0)
                    gmsh.model.mesh.field.setNumber(5, "DistMax", 6.0)

                    gmsh.model.mesh.field.add("Min", 6)
                    gmsh.model.mesh.field.setNumbers(6, "FieldsList", [3, 5])
                    bg = 6
                else:
                    bg = 3
            else:
                bg = 3

            gmsh.model.mesh.field.setAsBackgroundMesh(bg)

        min_allowed = min(
            face_min_size if surface_tags else mesh_size * 0.5,
            fine_size if surface_tags else mesh_size * 0.5
        ) * 0.8
        gmsh.option.setNumber("Mesh.MeshSizeMin", min_allowed)
        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)

        gmsh.model.mesh.generate(3)

        # Report quality
        print("Mesh quality:")
        compute_mesh_quality()

        gmsh.write(output_mesh)
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    targets = [
        ("violin_body.step", "violin_body.msh"),
        ("violin_cavity.step", "violin_cavity.msh"),
    ]
    any_done = False
    for step_input, mesh_output in targets:
        if os.path.exists(step_input):
            print(f"Generating mesh for {step_input} -> {mesh_output}")
            generate_mesh(step_input, mesh_output)
            any_done = True
        else:
            print(f"File {step_input} not found, skipping.")
    if any_done:
        print("Mesh generation complete.")
    else:
        print("No input STEP files found. Run cad/violin.py first.")
