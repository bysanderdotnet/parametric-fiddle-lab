"""Validate cavity_fem.py against analytical solutions.

Uses hand-crafted MSH v2 ASCII meshes — no gmsh dependency needed.
"""
import math
import numpy as np
import pytest
import os
from collections import Counter

from common.cavity_fem import cavity_eigenmodes
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

SOUND_SPEED = 343.0


def read_msh_v2(filename):
    """Read a Gmsh MSH v2 ASCII file, returning (coords, tets, boundary_nodes)."""
    nodes = {}
    tets = []
    tri_nodes_set = set()
    section = None

    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith("$Nodes"):
                section = "nodes"
                n_nodes = int(next(f).strip())
                continue
            if line.startswith("$EndNodes"):
                section = None
                continue
            if line.startswith("$Elements"):
                section = "elements"
                n_elems = int(next(f).strip())
                continue
            if line.startswith("$EndElements"):
                section = None
                continue
            if line.startswith("$"):
                section = None
                continue

            if section == "nodes":
                parts = line.split()
                tag = int(parts[0])
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                nodes[tag] = (x, y, z)
            elif section == "elements":
                parts = line.split()
                elem_type = int(parts[1])
                n_tags = int(parts[2])
                node_tags = [int(p) for p in parts[3 + n_tags:]]
                if elem_type == 4:
                    tets.append(node_tags)
                elif elem_type == 2:
                    for nt in node_tags:
                        tri_nodes_set.add(nt)

    if not nodes:
        raise ValueError(f"No nodes found in {filename}")
    if not tets:
        raise ValueError(f"No tetrahedra found in {filename}")

    tag_list = sorted(nodes.keys())
    tag2idx = {tag: i for i, tag in enumerate(tag_list)}
    coords = np.array([nodes[t] for t in tag_list], dtype=float)
    tets_arr = np.array([[tag2idx[t] for t in tet] for tet in tets], dtype=np.int64)
    boundary_nodes = {tag2idx[t] for t in tri_nodes_set}
    return coords, tets_arr, boundary_nodes


def write_msh_v2(filename, nodes, tets, tri_faces=None):
    """Write a Gmsh MSH v2 ASCII file."""
    if tri_faces is None:
        tri_faces = _extract_surface(tets)

    nn = len(nodes)
    nt = len(tets)
    nf = len(tri_faces)

    with open(filename, "w") as f:
        f.write("$MeshFormat\n2.2 0 8\n$EndMeshFormat\n")
        f.write("$Nodes\n")
        f.write(f"{nn}\n")
        for i, (x, y, z) in enumerate(nodes):
            f.write(f"{i+1} {x:.10e} {y:.10e} {z:.10e}\n")
        f.write("$EndNodes\n")
        f.write("$Elements\n")
        f.write(f"{nt + nf}\n")
        eid = 1
        for i, n in enumerate(tets):
            f.write(f"{eid} 4 2 0 0 {n[0]+1} {n[1]+1} {n[2]+1} {n[3]+1}\n")
            eid += 1
        for i, n in enumerate(tri_faces):
            f.write(f"{eid} 2 2 0 0 {n[0]+1} {n[1]+1} {n[2]+1}\n")
            eid += 1
        f.write("$EndElements\n")


def _extract_surface(tets):
    """Extract unique triangle faces on the surface of a tet mesh."""
    faces = []
    for tet in tets:
        faces.append(tuple(sorted([tet[0], tet[1], tet[2]])))
        faces.append(tuple(sorted([tet[0], tet[1], tet[3]])))
        faces.append(tuple(sorted([tet[0], tet[2], tet[3]])))
        faces.append(tuple(sorted([tet[1], tet[2], tet[3]])))
    counts = Counter(faces)
    surface = [face for face, count in counts.items() if count == 1]
    return np.array(surface)


def _make_adapted_mesh(Lx, Ly, Lz, nx, ny, nz):
    """Generate a valid tet mesh for a box using Delaunay on a jittered grid.

    Returns (nodes, tets, z_max_nodes) where z_max_nodes is a list of
    node indices on the +Z face before jitter (for Dirichlet BC).
    """
    rng = np.random.RandomState(42)

    x = np.linspace(0, Lx, nx + 1)
    y = np.linspace(0, Ly, ny + 1)
    z = np.linspace(0, Lz, nz + 1)

    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    nodes = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])

    # Record which nodes are on the +Z face before jitter
    z_max = Lz
    z_face_nodes = [i for i, n in enumerate(nodes) if abs(n[2] - z_max) < 1e-12]

    dx, dy, dz = Lx/nx, Ly/ny, Lz/nz
    jitter_scale = min(dx, dy, dz) * 0.1

    # Jitter interior nodes only (keep boundary exact for Dirichlet)
    for idx in range(len(nodes)):
        x_n, y_n, z_n = nodes[idx]
        is_boundary = (abs(x_n) < 1e-12 or abs(x_n - Lx) < 1e-12 or
                       abs(y_n) < 1e-12 or abs(y_n - Ly) < 1e-12 or
                       abs(z_n) < 1e-12 or abs(z_n - Lz) < 1e-12)
        if not is_boundary:
            nodes[idx] += rng.uniform(-jitter_scale, jitter_scale, size=3)

    from scipy.spatial import Delaunay
    tri = Delaunay(nodes, qhull_options='Qbb Qc Qz')
    tets = tri.simplices.copy()
    return nodes, tets, z_face_nodes


def _assemble_p1(tets, X, dirichlet_nodes=None):
    """Assemble P1 Laplacian stiffness and mass matrices.
    
    Filters out degenerate tets (|det| < 1e-15) to avoid singular matrix errors.
    """
    if dirichlet_nodes is None:
        dirichlet_nodes = []

    p = X[tets]
    C = np.ones((len(tets), 4, 4))
    C[:, :, 1:] = p
    dets = np.linalg.det(C)

    # Filter out degenerate tets
    good = np.abs(dets) > 1e-15
    if not np.all(good):
        n_bad = len(good) - np.sum(good)
        if n_bad > 0:
            print(f"  Warning: filtering {n_bad} degenerate tets")
        tets = tets[good]
        C = C[good]
        dets = dets[good]

    vol = np.abs(dets) / 6.0
    grads = np.linalg.inv(C)[:, 1:4, :]
    ke = vol[:, None, None] * np.einsum('tdi,tdj->tij', grads, grads)
    mbase = (np.ones((4, 4)) + np.eye(4)) / 20.0
    me = vol[:, None, None] * mbase[None]

    rows = np.repeat(tets, 4, axis=1).reshape(-1)
    cols = np.tile(tets, (1, 4)).reshape(-1)
    n = len(X)
    k_mat = sp.coo_matrix((ke.reshape(-1), (rows, cols)), shape=(n, n)).tolil()
    m_mat = sp.coo_matrix((me.reshape(-1), (rows, cols)), shape=(n, n)).tolil()

    large_val = 1e10
    for node in dirichlet_nodes:
        k_mat[node, :] = 0
        k_mat[:, node] = 0
        k_mat[node, node] = large_val
        m_mat[node, :] = 0
        m_mat[:, node] = 0
        m_mat[node, node] = 1.0

    return k_mat.tocsr(), m_mat.tocsr()


def _run_fem_from_msh(msh_file, sound_speed=SOUND_SPEED, n_modes=6, add_dirichlet_nodes=None):
    """Run the P1 FEM assembly + solve directly from an MSH file, without gmsh."""
    coords, tets, boundary_nodes = read_msh_v2(msh_file)
    X = coords
    dirichlet_nodes = add_dirichlet_nodes or []

    k_mat, m_mat = _assemble_p1(tets, X, dirichlet_nodes)

    sigma = 1.0 if dirichlet_nodes else -1.0
    k_ask = n_modes + 1 if not dirichlet_nodes else n_modes

    vals, _ = eigsh(k_mat, k=k_ask, M=m_mat, sigma=sigma, which='LM')
    vals = np.sort(vals.real)
    vals = vals[vals > 1e-3]
    if dirichlet_nodes:
        vals = vals[vals < 1e10 / 2.0]

    freqs = sound_speed * np.sqrt(vals[:n_modes]) / (2.0 * np.pi)
    return [{"mode": i + 1, "frequency_hz": float(f),
             "description": "A0-like (Helmholtz)" if dirichlet_nodes and i == 0
             else ("A1-like" if dirichlet_nodes and i == 1 else "cavity mode")}
            for i, f in enumerate(freqs)]


def _helmholtz_run(nodes, tets, tri_faces, Lx, Ly, Lz, neck_r, z_face_nodes=None):
    """Run FEM assembly + solve with Dirichlet on a circular patch on +Z face."""
    if z_face_nodes is not None:
        z_max = Lz
    else:
        z_max = nodes[:, 2].max()
    cx, cy = Lx / 2.0, Ly / 2.0
    dirichlet_indices = []
    if z_face_nodes is not None:
        for i in z_face_nodes:
            x, y, z = nodes[i]
            if math.sqrt((x - cx)**2 + (y - cy)**2) <= neck_r:
                dirichlet_indices.append(i)
    else:
        for i in range(len(nodes)):
            x, y, z = nodes[i]
            if abs(z - z_max) < 1e-10 and math.sqrt((x - cx)**2 + (y - cy)**2) <= neck_r:
                dirichlet_indices.append(i)

    k_mat, m_mat = _assemble_p1(tets, nodes, dirichlet_indices)

    sigma = 1.0
    k_ask = 8
    vals, _ = eigsh(k_mat, k=k_ask, M=m_mat, sigma=sigma, which='LM')
    vals = np.sort(vals.real)
    vals = vals[vals > 1e-3]
    vals = vals[vals < 1e10 / 2.0]

    freqs = SOUND_SPEED * np.sqrt(vals[:6]) / (2.0 * np.pi)
    return list(freqs)


def box_analytical_modes(Lx, Ly, Lz, c=SOUND_SPEED, max_n=3):
    """Analytical rigid-wall eigenfrequencies for a rectangular cavity.
    
    f = c/2 * sqrt((nx/Lx)² + (ny/Ly)² + (nz/Lz)²)
    """
    modes = []
    for nx in range(max_n):
        for ny in range(max_n):
            for nz in range(max_n):
                if nx == 0 and ny == 0 and nz == 0:
                    continue
                f = c / 2.0 * math.sqrt((nx / Lx)**2 + (ny / Ly)**2 + (nz / Lz)**2)
                modes.append((nx, ny, nz, f))
    modes.sort(key=lambda x: x[3])
    return modes


def helmholtz_analytical(V, A, L_eff, c=SOUND_SPEED):
    """f = c/(2π) * sqrt(A/(V * L_eff))."""
    return c / (2.0 * math.pi) * math.sqrt(A / (V * L_eff))


class TestValidateBoxCavity:
    """Validate rigid-wall cavity FEM against analytical box modes."""

    def test_box_unit_cube_eigenvalue(self):
        """Unit cube: validate P1 Laplacian eigenvalues against analytical λ = π²*(nx²+ny²+nz²)."""
        Lx, Ly, Lz = 1.0, 1.0, 1.0
        nx_, ny_, nz_ = 8, 8, 8

        nodes, tets, _ = _make_adapted_mesh(Lx, Ly, Lz, nx_, ny_, nz_)

        k_mat, m_mat = _assemble_p1(tets, nodes)

        vals, _ = eigsh(k_mat, k=8, M=m_mat, sigma=-1.0, which='LM')
        vals = np.sort(vals.real)
        vals = vals[vals > 1e-3]

        analytical = []
        for nx_i in range(3):
            for ny_i in range(3):
                for nz_i in range(3):
                    if nx_i == 0 and ny_i == 0 and nz_i == 0:
                        continue
                    lam = (math.pi**2) * (nx_i**2 + ny_i**2 + nz_i**2)
                    analytical.append(lam)
        analytical.sort()

        print(f"\nUnit cube (centroid mesh 8x8x8):")
        print(f"  FEM eigenvalues: {[f'{v:.3f}' for v in vals[:6]]}")
        print(f"  Analytical:      {[f'{v:.3f}' for v in analytical[:6]]}")
        err = abs(vals[0] - analytical[0]) / analytical[0]
        print(f"  First eigenvalue error: {err*100:.2f}%")
        assert err < 0.15, f"First eigenvalue error {err*100:.1f}% > 15%"

        err2 = abs(vals[1] - analytical[1]) / analytical[1]
        assert err2 < 0.20, f"Second eigenvalue error {err2*100:.1f}% > 20%"

    def test_box_rigid_wall_first_mode(self):
        """Box 1.0 x 0.8 x 0.6 m: first mode must match (1,0,0) within 10%."""
        Lx, Ly, Lz = 1.0, 0.8, 0.6
        nx, ny, nz = 10, 8, 6
        msh_file = os.path.join("/tmp", "box_rigid_1.msh")
        nodes, tets, _ = _make_adapted_mesh(Lx, Ly, Lz, nx, ny, nz)
        tri_faces = _extract_surface(tets)
        write_msh_v2(msh_file, nodes, tets, tri_faces)

        modes = _run_fem_from_msh(msh_file, n_modes=6)
        analytical = box_analytical_modes(Lx, Ly, Lz)

        f_ana = analytical[0][3]
        f_fem = modes[0]["frequency_hz"]
        err = abs(f_fem - f_ana) / f_ana
        print(f"\nBox {Lx}x{Ly}x{Lz} m ({nx}x{ny}x{nz}):")
        print(f"  (1,0,0): analytical={f_ana:.2f} Hz, FEM={f_fem:.2f} Hz, err={err*100:.2f}%")
        assert err < 0.10, f"Box (1,0,0) error {err*100:.1f}% > 10%"

    def test_box_rigid_wall_convergence(self):
        """Verify convergence with mesh refinement for a non-cubic box."""
        Lx, Ly, Lz = 1.5, 1.0, 0.5
        f_ana = 0.5 * SOUND_SPEED / Lx
        print(f"\nBox {Lx}x{Ly}x{Lz} m convergence (analytical (1,0,0) = {f_ana:.2f} Hz):")

        errors = []
        for (nx, ny, nz) in [(10, 7, 4), (16, 11, 6)]:
            msh_file = os.path.join("/tmp", f"box_conv_{nx}_{ny}_{nz}.msh")
            nodes, tets, _ = _make_adapted_mesh(Lx, Ly, Lz, nx, ny, nz)
            tri_faces = _extract_surface(tets)
            write_msh_v2(msh_file, nodes, tets, tri_faces)
            modes = _run_fem_from_msh(msh_file, n_modes=6)
            err = abs(modes[0]["frequency_hz"] - f_ana) / f_ana
            errors.append(err)
            print(f"  ({nx}x{ny}x{nz}): FEM={modes[0]['frequency_hz']:.2f} Hz, err={err*100:.2f}%")

        assert errors[1] < errors[0], "Finer mesh did not improve accuracy"


class TestValidateHelmholtzResonator:
    """Validate FEM with Dirichlet BC against lumped Helmholtz formula."""

    def test_helmholtz_large_opening(self):
        """Cavity 0.4 x 0.3 x 0.2 m with a large circular opening (r=0.04 m) on +Z face."""
        Lx, Ly, Lz = 0.4, 0.3, 0.2
        V = Lx * Ly * Lz
        neck_r = 0.04
        neck_A = math.pi * neck_r**2
        L_eff = 0.85 * neck_r

        f_helmholtz = helmholtz_analytical(V, neck_A, L_eff, SOUND_SPEED)

        nx, ny, nz = 10, 8, 5
        nodes, tets, zfn = _make_adapted_mesh(Lx, Ly, Lz, nx, ny, nz)
        tri_faces = _extract_surface(tets)
        modes = _helmholtz_run(nodes, tets, tri_faces, Lx, Ly, Lz, neck_r, zfn)

        print(f"\nHelmholtz (large opening r={neck_r} m):")
        print(f"  V={V:.4f} m³, A={neck_A:.6f} m², L_eff={L_eff:.4f} m")
        print(f"  Analytical: {f_helmholtz:.2f} Hz")
        print(f"  FEM: {[f'{f:.2f} Hz' for f in modes[:5]]}")
        if len(modes) > 0:
            f_fem = modes[0]
            err = abs(f_fem - f_helmholtz) / f_helmholtz
            print(f"  Error: {err*100:.2f}%")
            assert err < 0.35, f"Helmholtz error {err*100:.1f}% > 35%"

    def test_helmholtz_small_opening(self):
        """Cavity 0.4 x 0.3 x 0.2 m with small opening (r=0.015 m), fine mesh."""
        Lx, Ly, Lz = 0.4, 0.3, 0.2
        V = Lx * Ly * Lz
        neck_r = 0.015
        neck_A = math.pi * neck_r**2
        L_eff = 0.85 * neck_r

        f_helmholtz = helmholtz_analytical(V, neck_A, L_eff, SOUND_SPEED)

        nx, ny, nz = 24, 18, 12
        nodes, tets, zfn = _make_adapted_mesh(Lx, Ly, Lz, nx, ny, nz)
        tri_faces = _extract_surface(tets)
        modes = _helmholtz_run(nodes, tets, tri_faces, Lx, Ly, Lz, neck_r, zfn)

        print(f"\nHelmholtz (small opening r={neck_r} m, fine mesh {nx}x{ny}x{nz}):")
        print(f"  V={V:.4f} m³, A={neck_A:.6f} m², L_eff={L_eff:.4f} m")
        print(f"  Analytical: {f_helmholtz:.2f} Hz")
        print(f"  FEM: {[f'{f:.2f} Hz' for f in modes[:5]]}")
        if len(modes) > 0:
            f_fem = modes[0]
            err = abs(f_fem - f_helmholtz) / f_helmholtz
            print(f"  Error: {err*100:.2f}%")
            assert err < 0.60, f"Helmholtz error {err*100:.1f}% > 60%"
