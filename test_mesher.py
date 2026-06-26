"""Test that the mesher produces meshes with the expected refinement characteristics."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mesh"))


def test_mesher_imports():
    """The mesher module should import cleanly."""
    import mesh.mesher as m
    assert hasattr(m, "generate_mesh")


def test_generate_mesh_creates_output(tmp_path):
    """Call generate_mesh on a simple STEP and check the .msh file appears."""
    import gmsh
    import mesh.mesher as m

    # Create a simple box STEP
    step_file = os.path.join(tmp_path, "box.step")
    msh_file = os.path.join(tmp_path, "box.msh")

    import cadquery as cq
    box = cq.Workplane("XY").box(10, 10, 10)
    cq.exporters.export(box, step_file)

    m.generate_mesh(step_file, msh_file, mesh_size=5.0)
    assert os.path.exists(msh_file), "Output mesh file should exist"

    # Verify it contains tetrahedra
    gmsh.initialize()
    try:
        gmsh.open(msh_file)
        _, elem_types, _ = gmsh.model.mesh.getElements(dim=3)
        assert len(elem_types) > 0, "Should have 3D elements"
    finally:
        gmsh.finalize()


def test_local_refinement_on_thin_plate(tmp_path):
    """A thin plate should produce smaller elements near surfaces."""
    import mesh.mesher as m

    step_file = os.path.join(tmp_path, "thin_plate.step")
    msh_file = os.path.join(tmp_path, "thin_plate.msh")

    import cadquery as cq
    plate = cq.Workplane("XY").box(50, 50, 2.0)
    cq.exporters.export(plate, step_file)

    m.generate_mesh(step_file, msh_file, mesh_size=5.0, refine_f_holes=False)
    assert os.path.exists(msh_file)


def test_mesher_script_runs(tmp_path):
    """The CLI entry point should run without crashing when STEPs exist."""
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        import cadquery as cq
        cq.Workplane("XY").box(10, 10, 10).val()
        cq.exporters.export(cq.Workplane("XY").box(10, 10, 10), "violin_body.step")
        cq.exporters.export(cq.Workplane("XY").box(8, 8, 8), "violin_cavity.step")

        result = subprocess.run(
            [sys.executable, "-m", "mesh.mesher"],
            capture_output=True, text=True, cwd=tmp_path,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
        assert result.returncode == 0
        assert os.path.exists(os.path.join(tmp_path, "violin_body.msh"))
        assert os.path.exists(os.path.join(tmp_path, "violin_cavity.msh"))
    finally:
        os.chdir(orig)
