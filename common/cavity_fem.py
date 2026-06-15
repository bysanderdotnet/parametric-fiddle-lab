"""Acoustic air-cavity eigenmodes via P1 tetrahedral FEM.

Elmer cannot run our scalar acoustic eigenanalysis, so cavity modes are solved
here directly: assemble the P1 Laplacian stiffness/mass on the gmsh tet mesh and
solve the generalized eigenproblem  K f = (omega/c)^2 M f  with rigid (Neumann)
walls. The zero constant-pressure mode is dropped; the rest are the rigid-wall
internal cavity resonances. The true A0 Helmholtz mode needs the f-hole openings
and is not modeled here.

Elmer scalar-eigen status (tested 2026-06-15, installed PPA 26.2 AND a from-
source build of release-26.2.1 in /opt/elmer-26.2.1 -- identical behavior):
  - The old "segfault at AddEquationSolution/AddSolvers setup" is GONE; scalar
    eigen now reaches the solver.
  - HeatSolve / HelmholtzSolve eigen (Steady state) still fail: ARPACK
    DNAUPD info=-9, because the mass ("B") matrix is not assembled in steady
    state -> zero starting vector. A Dirichlet BC + eigen shift do not help
    (M is genuinely zero). StressSolve works only because elasticity modal
    analysis always builds its mass matrix.
  - HeatSolve eigen in Transient mode SEGFAULTs in add1stordertime (a separate
    eigen+transient code path bug).
So this Python fallback stays until a custom solver assembles the scalar mass
matrix, or upstream fixes scalar-eigen mass assembly. Note: the elmer-csc PPA
package is labelled 9.0-* but the binary is really v26.2.
"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import json
import math
import os


def is_in_f_hole(x, y, p):
    dx = p["f_hole_spacing"] / 2.0 + p["f_hole_x_offset"]
    dy = p["f_hole_y_offset"]

    angle_rad = math.radians(p["f_hole_angle"])
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)

    for cx in [dx, -dx]:
        tx = x - cx
        ty = y - dy

        rx = tx * c + ty * s
        ry = -tx * s + ty * c

        if p["f_hole_profile"] == "slot":
            half_len = p["f_hole_length"] / 2.0
            half_width = p["f_hole_width"] / 2.0

            if abs(rx) <= half_len and abs(ry) <= half_width:
                return True
            if abs(rx) > half_len:
                cx2 = half_len * np.sign(rx)
                if (rx - cx2)**2 + ry**2 <= half_width**2:
                    return True
        else:
            half_len = (p["f_hole_length"] * 0.8) / 2.0
            half_width = p["f_hole_width"] / 2.0
            if abs(rx) <= half_len and abs(ry) <= half_width:
                return True
            if abs(rx) > half_len:
                cx2 = half_len * np.sign(rx)
                if (rx - cx2)**2 + ry**2 <= half_width**2:
                    return True

            dx_top = p["f_hole_length"] * 0.4
            if (rx - dx_top)**2 + ry**2 <= p["f_hole_top_radius"]**2:
                return True
            if (rx + dx_top)**2 + ry**2 <= p["f_hole_bottom_radius"]**2:
                return True
    return False


def _read_tets(msh_file):
    """Return (node coords (Nn,3), tet connectivity (Nt,4), and boundary node indices) from a gmsh mesh."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.open(msh_file)
        ntags, ncoords, _ = gmsh.model.mesh.getNodes()
        coords = np.array(ncoords).reshape(-1, 3)
        tag2idx = {t: i for i, t in enumerate(ntags)}
        _, enodes = gmsh.model.mesh.getElementsByType(4)  # 4-node tetrahedra

        _, tri_nodes = gmsh.model.mesh.getElementsByType(2) # 3-node triangles (boundary)
        tri_nodes = np.array([tag2idx[t] for t in tri_nodes], dtype=np.int64)
        boundary_nodes = set(tri_nodes.flatten())
    finally:
        gmsh.finalize()
    tets = np.array([tag2idx[t] for t in enodes], dtype=np.int64).reshape(-1, 4)
    return coords, tets, boundary_nodes


def cavity_eigenmodes(msh_file, sound_speed=343.0, n_modes=6, mesh_scale=1e-3):
    """Lowest cavity resonances (Hz) of the air volume in msh_file, including A0 Helmholtz mode."""
    coords, tets, boundary_nodes = _read_tets(msh_file)
    X = coords * mesh_scale  # gmsh mesh is in mm; FEM works in metres

    # Read violin parameters to identify F-holes
    params_file = os.path.join(os.path.dirname(msh_file), "violin_body.json")
    dirichlet_nodes = []
    if os.path.exists(params_file):
        with open(params_file) as f:
            p = json.load(f)
        for i in boundary_nodes:
            x, y, z = coords[i]
            if z > p["rib_height"] * 0.8 and is_in_f_hole(x, y, p):
                dirichlet_nodes.append(i)

    # Per-tet P1 shape-function gradients (constant) and volume from the
    # barycentric coefficient matrix C; grad(lambda_i) = rows 1..3 of inv(C).
    p = X[tets]                                   # (Nt,4,3)
    C = np.ones((len(tets), 4, 4))
    C[:, :, 1:] = p
    vol = np.abs(np.linalg.det(C)) / 6.0
    grads = np.linalg.inv(C)[:, 1:4, :]           # (Nt,3,4)
    ke = vol[:, None, None] * np.einsum('tdi,tdj->tij', grads, grads)
    mbase = (np.ones((4, 4)) + np.eye(4)) / 20.0  # consistent tet mass
    me = vol[:, None, None] * mbase[None]

    rows = np.repeat(tets, 4, axis=1).reshape(-1)
    cols = np.tile(tets, (1, 4)).reshape(-1)
    n = len(X)
    k_mat = sp.coo_matrix((ke.reshape(-1), (rows, cols)), shape=(n, n)).tolil()
    m_mat = sp.coo_matrix((me.reshape(-1), (rows, cols)), shape=(n, n)).tolil()

    # Apply Dirichlet boundary conditions (P=0 at F-holes)
    large_val = 1e10
    for node in dirichlet_nodes:
        k_mat[node, :] = 0
        k_mat[:, node] = 0
        k_mat[node, node] = large_val

        m_mat[node, :] = 0
        m_mat[:, node] = 0
        m_mat[node, node] = 1.0

    k_mat = k_mat.tocsr()
    m_mat = m_mat.tocsr()

    # Shift-invert near 0 (sigma=1.0 keeps K - sigma*M SPD)
    # If there are no Dirichlet nodes, we use sigma=-1.0 to avoid the singular zero mode.
    sigma = 1.0 if dirichlet_nodes else -1.0
    k_ask = n_modes + 1 if not dirichlet_nodes else n_modes

    vals, _ = eigsh(k_mat, k=k_ask, M=m_mat, sigma=sigma, which='LM')
    vals = np.sort(vals.real)

    # Filter out spurious high eigenvalues and the constant mode (if rigid)
    vals = vals[vals > 1e-3]
    if dirichlet_nodes:
        vals = vals[vals < large_val / 2.0]

    freqs = sound_speed * np.sqrt(vals[:n_modes]) / (2.0 * np.pi)
    return [{"mode": i + 1, "frequency_hz": float(f),
             "description": "A0-like (Helmholtz)" if dirichlet_nodes and i == 0 else ("A1-like" if dirichlet_nodes and i == 1 else "cavity mode")}
            for i, f in enumerate(freqs)]
