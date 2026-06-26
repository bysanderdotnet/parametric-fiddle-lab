import os
import sys
import math

sys.path.insert(0, os.path.dirname(__file__))
from mesh import mesher


def test_thickness_limited_size():
    assert abs(mesher._thickness_limited_size(4.0) - 4.0/3.0) < 1e-6
    assert abs(mesher._thickness_limited_size(12.0) - mesher.COARSE_SIZE) < 1e-6
    assert abs(mesher._thickness_limited_size(0.5) - mesher.REFINE_SIZE) < 1e-6


def test_refine_size_constants():
    assert 0.5 <= mesher.REFINE_SIZE <= 1.0
    assert 2.0 <= mesher.COARSE_SIZE <= 3.0


def test_generate_mesh_no_file():
    try:
        mesher.generate_mesh("nonexistent.step", "out.msh")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


def test_generate_mesh_basic():
    try:
        import gmsh
    except ImportError:
        pytest.skip("gmsh not installed")

    step_file = "violin_body.step"
    if not os.path.exists(step_file):
        pytest.skip(f"{step_file} not found")

    output = "/tmp/test_violin_body.msh"
    try:
        mesher.generate_mesh(step_file, output, use_refinement=True)
        assert os.path.exists(output)

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(output)

        element_types, element_tags, element_nodes = gmsh.model.mesh.getElements(dim=3)
        total_3d = sum(len(t) for t in element_tags)
        assert total_3d > 0, "No 3D elements"

        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
        assert len(node_tags) > 0, "No nodes"

        coords = list(node_coords)
        coord_map = {}
        for i, tag in enumerate(node_tags):
            coord_map[tag] = (coords[3*i], coords[3*i+1], coords[3*i+2])

        min_h = float('inf')
        for etype, etags, enodes in zip(element_types, element_tags, element_nodes):
            npe_map = {1: 2, 2: 3, 3: 4, 4: 10, 5: 6, 6: 5, 7: 3, 8: 6}
            npe = npe_map.get(etype, 8)
            for i in range(0, len(enodes), npe):
                elem_nodes = enodes[i:i+npe]
                verts = [coord_map[n] for n in elem_nodes if n in coord_map]
                if len(verts) >= 4:
                    for j in range(4):
                        for k in range(j+1, 4):
                            d = sum((verts[j][d]-verts[k][d])**2 for d in range(3))
                            h = math.sqrt(d)
                            if h < min_h:
                                min_h = h

        print(f"3D elements: {total_3d}, min edge: {min_h:.4f}")

        quality = gmsh.model.mesh.getQuality()
        if quality:
            min_q = min(quality)
            assert min_q >= 0.0, f"Negative quality: {min_q}"

        gmsh.finalize()
    finally:
        if os.path.exists(output):
            os.remove(output)


if __name__ == "__main__":
    import traceback
    tests = [
        test_thickness_limited_size,
        test_refine_size_constants,
        test_generate_mesh_no_file,
    ]
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except Exception as e:
            print(f"FAIL: {t.__name__}: {e}")
            traceback.print_exc()
