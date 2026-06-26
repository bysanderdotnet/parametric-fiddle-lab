import os

PLATE_THICKNESS_DEFAULT = 4.0
REFINE_SIZE = 0.5
COARSE_SIZE = 3.0


def _thickness_limited_size(thickness):
    return max(REFINE_SIZE, min(COARSE_SIZE, thickness / 3.0))


def generate_mesh(step_file, output_mesh, mesh_size=COARSE_SIZE,
                  plate_thickness=PLATE_THICKNESS_DEFAULT, use_refinement=True):
    if not os.path.exists(step_file):
        raise FileNotFoundError(f"Input file not found: {step_file}")

    import gmsh

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)

    try:
        gmsh.model.occ.importShapes(step_file)
        gmsh.model.occ.synchronize()

        if use_refinement:
            _add_mesh_size_fields(gmsh, plate_thickness)
        else:
            clamped = _thickness_limited_size(plate_thickness)
            gmsh.option.setNumber("Mesh.MeshSizeMin", REFINE_SIZE)
            gmsh.option.setNumber("Mesh.MeshSizeMax", clamped)

        gmsh.model.mesh.generate(3)

        num_nodes = gmsh.model.mesh.getNodes()[0].shape[0]
        num_elements = gmsh.model.mesh.getElements()[0].shape[0]
        print(f"Mesh generated: {num_nodes} nodes, {num_elements} elements")

        gmsh.write(output_mesh)
    finally:
        gmsh.finalize()


def _add_mesh_size_fields(gmsh, plate_thickness):
    clamped_max = _thickness_limited_size(plate_thickness)

    gmsh.option.setNumber("Mesh.MeshSizeMin", REFINE_SIZE)
    gmsh.option.setNumber("Mesh.MeshSizeMax", clamped_max)

    groups = gmsh.model.getPhysicalGroups()
    f_hole_surfaces = []

    for dim, tag in groups:
        name = gmsh.model.getPhysicalName(dim, tag)
        if name and "f_hole" in name.lower():
            entities = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)
            f_hole_surfaces.extend(entities)

    if not f_hole_surfaces:
        for dim, tag in groups:
            name = gmsh.model.getPhysicalName(dim, tag)
            if dim == 2 and name and ("f" in name.lower() or "hole" in name.lower()):
                entities = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)
                f_hole_surfaces.extend(entities)

    field_list = []

    if f_hole_surfaces:
        gmsh.model.mesh.field.add("Distance", 1)
        gmsh.model.mesh.field.setNumbers(1, "SurfacesList", f_hole_surfaces)
        field_list.append(1)

    all_curves = [c[1] for c in gmsh.model.getEntities(1)]
    if all_curves:
        gmsh.model.mesh.field.add("Distance", 2)
        gmsh.model.mesh.field.setNumbers(2, "CurvesList", all_curves)
        field_list.append(2)

    if field_list:
        if len(field_list) > 1:
            gmsh.model.mesh.field.add("Min", 3)
            gmsh.model.mesh.field.setNumbers(3, "FieldsList", field_list)
            combined = 3
        else:
            combined = field_list[0]

        gmsh.model.mesh.field.add("Threshold", 4)
        gmsh.model.mesh.field.setNumber(4, "InField", combined)
        gmsh.model.mesh.field.setNumber(4, "SizeMin", REFINE_SIZE)
        gmsh.model.mesh.field.setNumber(4, "SizeMax", clamped_max)
        gmsh.model.mesh.field.setNumber(4, "DistMin", 0.0)
        gmsh.model.mesh.field.setNumber(4, "DistMax", 15.0)
        gmsh.model.mesh.field.setAsBackgroundMesh(4)


if __name__ == "__main__":
    targets = [
        ("violin_body.step", "violin_body.msh"),
        ("violin_cavity.step", "violin_cavity.msh"),
    ]
    any_done = False
    for step_input, mesh_output in targets:
        if os.path.exists(step_input):
            print(f"Generating mesh for {step_input} -> {mesh_output}")
            generate_mesh(step_input, mesh_output, use_refinement=True)
            any_done = True
        else:
            print(f"File {step_input} not found, skipping.")
    if any_done:
        print("Mesh generation complete.")
    else:
        print("No input STEP files found. Run cad/violin.py first.")
