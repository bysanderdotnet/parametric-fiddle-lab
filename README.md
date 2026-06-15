# Resonant Violin Lab

Resonant Violin Lab is a platform for building a parametric, simulatable, and optimizable design chain for 3D-printed violins. It aims to optimize the acoustic and structural properties of 3D-printed violins by treating geometry, slicing parameters, materials, and internal structure as tunable design variables.

## Overview

The project uses a pipeline architecture:
1.  **Parametric Generation:** Generating the geometry using code (CadQuery).
2.  **Slicing as Design:** Treating slicing parameters (infill, perimeters, modifiers) as design variables via Orca Slicer CLI.
3.  **Simulation:** Using structural and acoustic simulation to evaluate designs (eigenmodes, stress, cavity modes, etc.) using Gmsh, Elmer.
4.  **Optimization:** Iterating designs using bayesian optimization or evolutionary algorithms (Optuna, BoTorch).

## Directory Structure

*   `cad/` - Parametric violin generator
*   `profiles/` - Machine, process, and filament profiles
*   `slice/` - Orca Slicer wrappers and slice data export
*   `mesh/` - STEP to mesh conversion and quality checks
*   `sim_struct/` - Simulation of preload, deflection, stresses, and eigenmodes
*   `sim_acoustic/` - Simulation of cavity modes, radiation, and bridge mobility
*   `opt/` - Objective functions, optimization trials, and surrogate models
*   `data/` - Run logs, reference curves, and benchmark results
*   `docs/` - Literature, design notes, and decision logs

## Getting Started

Use `./AGENTS.sh help` to see available project commands.
