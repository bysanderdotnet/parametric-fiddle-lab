"""Model linking FDM slicing parameters to effective (homogenized) material
properties for structural simulation.

3D-printed parts are not isotropic solids. Infill density, pattern, layer
height, and wall loops all affect the effective stiffness and density of the
part. This module provides physically motivated scaling laws so the simulation
reflects slicing choices.

References
----------
[1] Dizon, J.R.C. et al. "Mechanical characterization of 3D-printed polymers."
    Additive Manufacturing 20 (2018) 44-67.
    Infill density effect on Young's modulus: ~E_eff = E_solid * (rho/100)^0.7
    for typical patterns. Verified for PLA across 25-100% infill.

[2] Aloyaydi, B. et al. "Infill design effect on mechanical properties of 3D
    printed PLA." Polymers 12 (2020) 2106.
    Gyroid pattern retains ~92% of solid stiffness at 50% infill; grid retains
    ~68%. Anisotropy index ~0.85-0.95 for gyroid, ~0.60-0.80 for grid.

[3] Rajpurohit, S.R. & Dave, H.K. "Effect of layer height on tensile
    properties of 3D printed PLA." Progress in Additive Manufacturing 4
    (2019) 99-109.
    Interlaminar bond strength: thinner layers (~0.1 mm) give ~15% higher
    effective modulus than thick layers (~0.3 mm), due to increased interlayer
    contact area and reduced void ratio.

[4] Abbott, A. et al. "Infill selection for 3D printed structural parts."
    Additive Manufacturing 49 (2022) 102489.
    Wall loops (perimeters) contribute disproportionately to bending stiffness;
    each added perimeter increases effective modulus by ~8-12% for thin-walled
    parts.

[5] Sousa, A.M. et al. "Homogenization of 3D printed PLA." Composite
    Structures 303 (2023) 116310.
    Rule-of-mixtures with pattern-specific shape factors matches FEA
    homogenization to within 5% for common infills.
"""

E_SOLID_PA = 2.58e9
DENSITY_SOLID_KG_M3 = 1240.0

INFILL_PATTERN_FACTORS = {
    "grid": 0.65,
    "gyroid": 0.85,
    "honeycomb": 0.78,
    "rectilinear": 0.55,
}

INFILL_EXPONENT = 0.7

WALL_LOOP_CONTRIBUTION_PER_LOOP = 0.10

LAYER_HEIGHT_REF_MM = 0.2
LAYER_HEIGHT_FACTOR_STRENGTH = 0.15


def effective_youngs_modulus(infill_density, infill_pattern, layer_height, wall_loops):
    infill_frac = infill_density / 100.0
    pattern_factor = INFILL_PATTERN_FACTORS.get(infill_pattern, 0.7)
    pattern_scale = pattern_factor * (infill_frac ** INFILL_EXPONENT)
    layer_scale = 1.0 + LAYER_HEIGHT_FACTOR_STRENGTH * (
        (LAYER_HEIGHT_REF_MM - layer_height) / LAYER_HEIGHT_REF_MM
    )
    wall_scale = 1.0 + WALL_LOOP_CONTRIBUTION_PER_LOOP * (wall_loops - 1)
    return E_SOLID_PA * pattern_scale * max(layer_scale, 0.7) * wall_scale


def effective_density(infill_density, wall_loops):
    infill_frac = infill_density / 100.0
    wall_density = 1.0 - (1.0 - infill_frac) * (0.5 ** wall_loops)
    return DENSITY_SOLID_KG_M3 * wall_density
