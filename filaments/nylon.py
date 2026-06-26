"""Bambu Nylon PA6/PA12-CF filament properties.

Source: Bambu Lab PA6-CF / PA12-CF Technical Data Sheets (V1.0).
Combined module covering both PA6 (standard Nylon) and PA12-CF (carbon-fiber filled).
Default values are PA6-CF (carbon-fiber reinforced Nylon 6).
Poisson ratio not in datasheet; typical Nylon-CF value (0.35) used.
"""

NAME = "Bambu PA6-CF"
DATASHEET = "Technical Data Sheets V1.0 (PA6-CF, PA12-CF)"

SPECIFICATIONS = {
    "diameter_mm": 1.75,
    "net_filament_weight_kg": 0.5,
    "spool_material": "PC",
    "spool_temp_resistance_c": 100,
    "spool_diameter_mm": 200,
    "spool_height_mm": 67,
}

PRINTING = {
    "dry_oven_temp_c": 80,
    "dry_oven_hours": 12,
    "dry_heatbed_temp_c": (90, 100),
    "dry_heatbed_hours": 12,
    "storage_humidity_pct_rh_max": 15,
    "nozzle_sizes_mm": [0.4, 0.6],
    "nozzle_temp_c": (260, 300),
    "bed_types": ["High Temperature Plate", "Textured PEI Plate"],
    "bed_surface_prep": "Glue",
    "bed_temp_c": (80, 100),
    "cooling_fan": False,
    "printing_speed_mm_s_max": 100,
    "retraction_length_mm": (0.4, 0.8),
    "retraction_speed_mm_s": (20, 40),
    "chamber_temp_c": (40, 60),
    "max_overhang_angle_deg": 35,
    "max_bridging_length_mm": 10,
    "support_material": "Support for PA",
    "anneal_temp_c": (90, 100),
    "anneal_hours": (4, 8),
}

PHYSICAL = {
    "density_g_cm3": 1.20,
    "melt_index_g_10min": (5.0, 1.5),
    "melting_temp_c": 220,
    "glass_transition_temp_c": 75,
    "crystallization_temp_c": 180,
    "vicat_softening_temp_c": 110,
    "heat_deflection_temp_c_1_8mpa": 100,
    "heat_deflection_temp_c_0_45mpa": 145,
    "saturated_water_absorption_pct": 1.5,
}

MECHANICAL = {
    "youngs_modulus_mpa_xy": (8500, 500),
    "youngs_modulus_mpa_z": (4500, 400),
    "tensile_strength_mpa_xy": (110, 10),
    "tensile_strength_mpa_z": (60, 8),
    "breaking_elongation_pct_xy": (3.0, 0.5),
    "breaking_elongation_pct_z": (2.0, 0.5),
    "bending_modulus_mpa_xy": (7500, 500),
    "bending_modulus_mpa_z": (4000, 400),
    "bending_strength_mpa_xy": (150, 15),
    "bending_strength_mpa_z": (90, 10),
    "impact_strength_kj_m2_xy": (30.0, 3.0),
    "impact_strength_kj_m2_xy_notched": (5.0, 1.0),
    "impact_strength_kj_m2_z": (15.0, 2.0),
}

CHEMICAL = {
    "odor": "Mild",
    "composition": "PA6 with carbon fiber reinforcement",
    "skin_hazards": "No hazard",
    "chemical_stability": "Hygroscopic — must be dried before printing",
    "solubility": "Insoluble in water",
    "resistance_acid": False,
    "resistance_alkali": True,
    "resistance_organic_solvent": True,
    "resistance_oil_grease": True,
    "flammable": True,
    "combustion_products": "Water, carbon oxides, nitrogen oxides",
}

SPECIMEN_TEST = {
    "nozzle_temp_c": 280,
    "bed_temp_c": 90,
    "printing_speed_mm_s": 60,
    "infill_density_pct": 100,
    "note": "Specimens dried at 80 C for 12 h before testing. Chamber heated to 50 C.",
}

DENSITY_KG_M3 = 1200.0
YOUNGS_MODULUS_PA = 8.5e9
POISSON_RATIO = 0.35

DENSITY_G_MM3 = PHYSICAL["density_g_cm3"] / 1000.0
