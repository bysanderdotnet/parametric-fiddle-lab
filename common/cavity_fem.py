"""Acoustic air-cavity eigenmodes via P1 tetrahedral FEM.

Elmer cannot run our scalar acoustic eigenanalysis, so cavity modes are solved
here directly: assemble the P1 Laplacian stiffness/mass on the gmsh tet mesh and
solve the generalized eigenproblem  K f = (omega/c)^2 M f  with rigid (Neumann)
walls. The zero constant-pressure mode is dropped; the rest are the rigid-wall
internal cavity resonances. The true A0 Helmholtz mode needs the f-hole openings
and is not modeled here.

Elmer eigen status (tested 2026-06-15, installed PPA 26.2 AND a from-source
build of release-26.2.1 in /opt/elmer-26.2.1 -- identical behavior):
  - On the REAL violin_cavity.msh, eigen analysis still SEGFAULTs at solver
    init: AddSolvers -> AddEquationSolution, MainUtils.F90:2619, a null deref
    SIZE(Solver % Matrix % Values) when Values is unassociated. This is the
    same AddEquationSolution/AddSolvers crash originally reported -> NOT fixed
    by 26.2.1.
  - It is NOT scalar-specific: vector StressSolve eigen crashes on this mesh
    too. It is NOT mesh size (a same-size 13k-node cube runs fine) and NOT the
    lower-dim boundary elements (-removelowdim does not help). It is specific
    to the cavity mesh content, which leaves Solver % Matrix % Values null.
  - A plain (non-eigen) solve on the same cavity mesh works.
  - A trivial cube DID survive setup and instead hit ARPACK DNAUPD info=-9
    (mass/"B" matrix not assembled in steady state) -- but that path is moot
    here because the violin mesh never reaches it.
So this Python fallback stays: a newer Elmer build alone does not fix the
crash on our actual geometry. Note: the elmer-csc PPA package is labelled
9.0-* but the binary is really v26.2.
"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh


def _read_tets(msh_file):
    """Return (node coords (Nn,3), tet connectivity (Nt,4)) from a gmsh mesh."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.open(msh_file)
        ntags, ncoords, _ = gmsh.model.mesh.getNodes()
        coords = np.array(ncoords).reshape(-1, 3)
        tag2idx = {t: i for i, t in enumerate(ntags)}
        _, enodes = gmsh.model.mesh.getElementsByType(4)  # 4-node tetrahedra
    finally:
        gmsh.finalize()
    tets = np.array([tag2idx[t] for t in enodes], dtype=np.int64).reshape(-1, 4)
    return coords, tets


def cavity_eigenmodes(msh_file, sound_speed=343.0, n_modes=6, mesh_scale=1e-3):
    """Lowest rigid-wall cavity resonances (Hz) of the air volume in msh_file."""
    coords, tets = _read_tets(msh_file)
    X = coords * mesh_scale  # gmsh mesh is in mm; FEM works in metres

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
    k_mat = sp.coo_matrix((ke.reshape(-1), (rows, cols)), shape=(n, n)).tocsr()
    m_mat = sp.coo_matrix((me.reshape(-1), (rows, cols)), shape=(n, n)).tocsr()

    # Shift-invert near 0 (sigma<0 keeps K - sigma*M SPD past the singular
    # constant mode); ask for one extra to absorb that zero mode.
    vals, _ = eigsh(k_mat, k=n_modes + 1, M=m_mat, sigma=-1.0, which='LM')
    vals = np.sort(vals.real)
    vals = vals[vals > 1e-3][:n_modes]            # drop constant-pressure mode
    freqs = sound_speed * np.sqrt(vals) / (2.0 * np.pi)
    return [{"mode": i + 1, "frequency_hz": float(f),
             "description": "rigid-wall cavity mode"}
            for i, f in enumerate(freqs)]
