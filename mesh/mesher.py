import gmsh
import os

def generate_mesh(step_file, output_mesh, mesh_size=5.0):
    """
    Generate a 3D mesh from a STEP file using Gmsh.
    """
    if not os.path.exists(step_file):
        raise FileNotFoundError(f"Input file not found: {step_file}")

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)

    try:
        # Load the step file
        gmsh.model.occ.importShapes(step_file)
        gmsh.model.occ.synchronize()

        # Set characteristic length (mesh size)
        gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)

        # Generate 3D mesh
        gmsh.model.mesh.generate(3)

        # Save to file
        gmsh.write(output_mesh)
    finally:
        gmsh.finalize()

if __name__ == "__main__":
    import sys
    # For testing when run directly
    step_input = "violin_body.step"
    mesh_output = "violin_body.msh"

    if os.path.exists(step_input):
        print(f"Generating mesh for {step_input} -> {mesh_output}")
        generate_mesh(step_input, mesh_output)
        print("Mesh generation complete.")
    else:
        print(f"File {step_input} not found. Run cad/violin.py first.")
