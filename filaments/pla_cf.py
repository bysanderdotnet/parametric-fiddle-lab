"""Bambu PLA-CF (Carbon Fiber reinforced PLA) filament properties.

Source: Bambu Lab PLA-CF Technical Data Sheet (V1.0).
Values are manufacturer typical values.
Poisson ratio not in datasheet; typical PLA-CF value (0.33) used.
"""

NAME = "Bambu PLA-CF"
DATASHEET = "Technical Data Sheet V1.0"

SPECIFICATIONS = {
    "diameter_mm": 1.75,
    "net_filament_weight_kg": 0.5,
    "spool_material": "ABS",
    "spool_temp_resistance_c": 70,
    "spool_diameter_mm": 200,
    "spool_height_mm": 67,
}

PRINTING = {
    "dry_oven_temp_c": 50,
    "dry_oven_hours": 8,
    "dry_heatbed_temp_c": (60, 70),
    "dry_heatbed_hours": 12,
    "storage_humidity_pct_rh_max": 20,
    "nozzle_sizes_mm": [0.4, 0.6],
    "nozzle_temp_c": (190, 230),
    "bed_types": ["Cool Plate", "High Temperature Plate", "Textured PEI Plate"],
    "bed_surface_prep": "Glue",
    "bed_temp_c": (35, 55),
    "cooling_fan": True,
    "printing_speed_mm_s_max": 200,
    "retraction_length_mm": (0.6, 1.0),
    "retraction_speed_mm_s": (20, 40),
    "chamber_temp_c": (25, 45),
    "max_overhang_angle_deg": 50,
    "max_bridging_length_mm": 20,
    "support_material": "Support for PLA",
    "anneal_temp_c": (50, 60),
    "anneal_hours": (6, 12),
}

PHYSICAL = {
    "density_g_cm3": 1.24,
    "melt_index_g_10min": (18.0, 3.0),
    "melting_temp_c": 160,
    "glass_transition_temp_c": 60,
    "crystallization_temp_c": None,
    "vicat_softening_temp_c": 57,
    "heat_deflection_temp_c_1_8mpa": 54,
    "heat_deflection_temp_c_0_45mpa": 57,
    "saturated_water_absorption_pct": 0.40,
}

MECHANICAL = {
    "youngs_modulus_mpa_xy": (5200, 400),
    "youngs_modulus_mpa_z": (3800, 350),
    "tensile_strength_mpa_xy": (45, 5),
    "tensile_strength_mpa_z": (35, 4),
    "breaking_elongation_pct_xy": (6.0, 1.0),
    "breaking_elongation_pct_z": (3.5, 0.8),
    "bending_modulus_mpa_xy": (5000, 400),
    "bending_modulus_mpa_z": (3600, 350),
    "bending_strength_mpa_xy": (80, 6),
    "bending_strength_mpa_z": (60, 5),
    "impact_strength_kj_m2_xy": (15.0, 2.0),
    "impact_strength_kj_m2_xy_notched": (4.5, 0.8),
    "impact_strength_kj_m2_z": (8.0, 1.0),
}

CHEMICAL = {
    "odor": "Odorless",
    "composition": "PLA with carbon fiber reinforcement",
    "skin_hazards": "No hazard",
    "chemical_stability": "Stable under normal storage and handling conditions",
    "solubility": "Insoluble in water",
    "resistance_acid": False,
    "resistance_alkali": False,
    "resistance_organic_solvent": False,
    "resistance_oil_grease": True,
    "flammable": True,
    "combustion_products": "Water, carbon oxides",
}

SPECIMEN_TEST = {
    "nozzle_temp_c": 220,
    "bed_temp_c": 35,
    "printing_speed_mm_s": 150,
    "infill_density_pct": 100,
    "note": "Specimens dried at 50 C for 8 h before testing.",
}

DENSITY_KG_M3 = 1240.0
YOUNGS_MODULUS_PA = 5.2e9
POISSON_RATIO = 0.33

DENSITY_G_MM3 = PHYSICAL["density_g_cm3"] / 1000.0
