"""Bambu PC (Polycarbonate) filament properties.

Source: Bambu Lab PC Technical Data Sheet (V1.0).
Values are manufacturer typical values.
Poisson ratio not in datasheet; typical PC value (0.37) used.
"""

NAME = "Bambu PC"
DATASHEET = "Technical Data Sheet V1.0"

SPECIFICATIONS = {
    "diameter_mm": 1.75,
    "net_filament_weight_kg": 1.0,
    "spool_material": "PC",
    "spool_temp_resistance_c": 100,
    "spool_diameter_mm": 200,
    "spool_height_mm": 67,
}

PRINTING = {
    "dry_oven_temp_c": 90,
    "dry_oven_hours": 8,
    "dry_heatbed_temp_c": (90, 100),
    "dry_heatbed_hours": 12,
    "storage_humidity_pct_rh_max": 15,
    "nozzle_sizes_mm": [0.4, 0.6, 0.8],
    "nozzle_temp_c": (260, 300),
    "bed_types": ["High Temperature Plate", "Textured PEI Plate"],
    "bed_surface_prep": "Glue",
    "bed_temp_c": (90, 100),
    "cooling_fan": False,
    "printing_speed_mm_s_max": 150,
    "retraction_length_mm": (0.4, 0.8),
    "retraction_speed_mm_s": (20, 40),
    "chamber_temp_c": (45, 65),
    "max_overhang_angle_deg": 40,
    "max_bridging_length_mm": 15,
    "support_material": "Support for PC",
    "anneal_temp_c": (100, 110),
    "anneal_hours": (2, 4),
}

PHYSICAL = {
    "density_g_cm3": 1.20,
    "melt_index_g_10min": (9.5, 2.0),
    "melting_temp_c": None,
    "glass_transition_temp_c": 110,
    "crystallization_temp_c": None,
    "vicat_softening_temp_c": 105,
    "heat_deflection_temp_c_1_8mpa": 100,
    "heat_deflection_temp_c_0_45mpa": 108,
    "saturated_water_absorption_pct": 0.20,
}

MECHANICAL = {
    "youngs_modulus_mpa_xy": (2400, 200),
    "youngs_modulus_mpa_z": (2000, 180),
    "tensile_strength_mpa_xy": (60, 6),
    "tensile_strength_mpa_z": (48, 5),
    "breaking_elongation_pct_xy": (20.0, 5.0),
    "breaking_elongation_pct_z": (10.0, 3.0),
    "bending_modulus_mpa_xy": (2500, 200),
    "bending_modulus_mpa_z": (2200, 180),
    "bending_strength_mpa_xy": (85, 7),
    "bending_strength_mpa_z": (65, 6),
    "impact_strength_kj_m2_xy": (40.0, 5.0),
    "impact_strength_kj_m2_xy_notched": (8.0, 1.5),
    "impact_strength_kj_m2_z": (20.0, 3.0),
}

CHEMICAL = {
    "odor": "Odorless",
    "composition": "Polycarbonate",
    "skin_hazards": "No hazard",
    "chemical_stability": "Stable under normal storage and handling conditions",
    "solubility": "Insoluble in water",
    "resistance_acid": True,
    "resistance_alkali": False,
    "resistance_organic_solvent": False,
    "resistance_oil_grease": True,
    "flammable": True,
    "combustion_products": "Water, carbon oxides",
}

SPECIMEN_TEST = {
    "nozzle_temp_c": 280,
    "bed_temp_c": 95,
    "printing_speed_mm_s": 100,
    "infill_density_pct": 100,
    "note": "Specimens dried at 90 C for 8 h before testing. Chamber heated to 55 C.",
}

DENSITY_KG_M3 = 1200.0
YOUNGS_MODULUS_PA = 2.40e9
POISSON_RATIO = 0.37

DENSITY_G_MM3 = PHYSICAL["density_g_cm3"] / 1000.0
