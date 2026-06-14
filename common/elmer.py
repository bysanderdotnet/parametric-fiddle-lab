"""Shared Elmer FEM helpers for the structural and acoustic simulations.

Both sims write an identical SIF skeleton differing only in the Solver and
Material blocks, run ElmerGrid + ElmerSolver, and parse the same EigenSolve
output. This module owns that common machinery.
"""
import math
import subprocess

# Everything but the Solver and Material blocks is identical across sims.
SIF_TEMPLATE = """Header
  CHECK KEYWORDS Warn
  Mesh DB "." "{mesh_dir}"
  Include Path ""
  Results Directory ""
End

Simulation
  Max Output Level = 5
  Coordinate System = Cartesian
  Coordinate Mapping(3) = 1 2 3
  Simulation Type = Steady state
  Steady State Max Iterations = 1
  Output Intervals(1) = 1
  Solver Input File = case.sif
  Post File = case.vtu
End

Constants
  Gravity(4) = 0 -1 0 9.82
  Stefan Boltzmann = 5.670374419e-08
  Permittivity of Vacuum = 8.85418781e-12
  Permeability of Vacuum = 1.25663706e-06
  Boltzmann Constant = 1.380649e-23
  Unit Charge = 1.6021766e-19
End

Body 1
  Target Bodies(1) = 1
  Name = "Body 1"
  Equation = 1
  Material = 1
End

{solver}

Equation 1
  Name = "Equation 1"
  Active Solvers(1) = 1
End

{material}
"""


def write_sif(sif_path, mesh_dir, solver, material):
    """Write a SIF file from the shared template + sim-specific blocks."""
    content = SIF_TEMPLATE.format(mesh_dir=mesh_dir, solver=solver.strip(), material=material.strip())
    with open(sif_path, "w") as f:
        f.write(content)


def parse_eigenmodes(stdout):
    """Extract eigenmodes from ElmerSolver EigenSolve output."""
    modes = []
    for line in stdout.split('\n'):
        if "EigenSolve:" in line and len(line.split()) >= 3:
            try:
                val = float(line.split()[2])
            except ValueError:
                continue
            freq = math.sqrt(val) / (2 * math.pi) if val > 0 else 0.0
            modes.append({"mode": len(modes) + 1, "frequency_hz": freq, "eigenvalue": val})
    return modes


def run_elmer(mesh_file, mesh_dir, sif_path, solver, material):
    """Run ElmerGrid + ElmerSolver, return parsed eigenmodes (or None)."""
    subprocess.run(["ElmerGrid", "14", "2", mesh_file, "-out", mesh_dir], check=True)
    write_sif(sif_path, mesh_dir, solver, material)
    result = subprocess.run(["ElmerSolver", sif_path], capture_output=True, text=True, check=True)
    modes = parse_eigenmodes(result.stdout)
    return modes or None
