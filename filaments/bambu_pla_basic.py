"""Bambu PLA Basic filament properties.

Source: docs/Bambu_PLA_Basic_Technical_Data_Sheet.pdf (Technical Data Sheet V3.0).
Values are manufacturer typical values "for design reference and comparison only".

SI convenience fields (for FEM, e.g. sim_struct/structural.py) at bottom.
Mechanical props are anisotropic (X-Y in-plane vs Z layer direction); FEM
defaults use X-Y. Tolerances kept as (value, plus_minus) tuples where given.
"""

NAME = "Bambu PLA Basic"
DATASHEET = "Technical Data Sheet V3.0"

# --- Specifications ---
SPECIFICATIONS = {
    "diameter_mm": 1.75,
    "net_filament_weight_kg": 1.0,
    "spool_material": "ABS",
    "spool_temp_resistance_c": 70,
    "spool_diameter_mm": 200,
    "spool_height_mm": 67,
}

# --- Recommended Printing Settings (ranges as (min, max)) ---
PRINTING = {
    "dry_oven_temp_c": 50,
    "dry_oven_hours": 8,
    "dry_heatbed_temp_c": (60, 70),      # X1 series printer heatbed
    "dry_heatbed_hours": 12,
    "storage_humidity_pct_rh_max": 20,
    "nozzle_sizes_mm": [0.2, 0.4, 0.6, 0.8],
    "nozzle_temp_c": (190, 230),
    "bed_types": ["Cool Plate", "High Temperature Plate", "Textured PEI Plate"],
    "bed_surface_prep": "Glue",
    "bed_temp_c": (35, 45),
    "cooling_fan": True,
    "printing_speed_mm_s_max": 300,
    "retraction_length_mm": (0.6, 1.0),
    "retraction_speed_mm_s": (20, 40),
    "chamber_temp_c": (25, 45),
    "max_overhang_angle_deg": 55,
    "max_bridging_length_mm": 30,
    "support_material": "Support for PLA",
    "anneal_temp_c": (50, 60),
    "anneal_hours": (6, 12),
}

# --- Physical Properties ((value, plus_minus) where tolerance given) ---
PHYSICAL = {
    "density_g_cm3": 1.24,                      # ISO 1183
    "melt_index_g_10min": (23.2, 3.5),          # 210 C, 2.16 kg
    "melting_temp_c": 160,                      # DSC, 10 C/min
    "glass_transition_temp_c": 60,              # DSC, 10 C/min
    "crystallization_temp_c": None,             # N/A
    "vicat_softening_temp_c": 57,               # ISO 306, GB/T 1633
    "heat_deflection_temp_c_1_8mpa": 54,        # ISO 75 1.8 MPa
    "heat_deflection_temp_c_0_45mpa": 57,       # ISO 75 0.45 MPa
    "saturated_water_absorption_pct": 0.43,     # 25 C, 55% RH
}

# --- Mechanical Properties ((value, plus_minus); _xy in-plane, _z layer dir) ---
MECHANICAL = {
    "youngs_modulus_mpa_xy": (2580, 220),       # ISO 527, GB/T 1040
    "youngs_modulus_mpa_z": (2060, 170),
    "tensile_strength_mpa_xy": (35, 4),
    "tensile_strength_mpa_z": (31, 3),
    "breaking_elongation_pct_xy": (12.2, 1.8),
    "breaking_elongation_pct_z": (7.5, 1.3),
    "bending_modulus_mpa_xy": (2750, 160),      # ISO 178, GB/T 9341
    "bending_modulus_mpa_z": (2370, 150),
    "bending_strength_mpa_xy": (76, 5),
    "bending_strength_mpa_z": (59, 6),
    "impact_strength_kj_m2_xy": (26.6, 2.8),    # ISO 179, GB/T 1043
    "impact_strength_kj_m2_xy_notched": (7.9, 1.2),
    "impact_strength_kj_m2_z": (13.8, 0.9),
}

# --- Other Physical and Chemical Properties ---
CHEMICAL = {
    "odor": "Odorless",
    "composition": "PLA",
    "skin_hazards": "No hazard",
    "chemical_stability": "Stable under normal storage and handling conditions",
    "solubility": "Insoluble in water",
    "resistance_acid": False,
    "resistance_alkali": False,
    "resistance_organic_solvent": False,        # not resistant to some organic solvents
    "resistance_oil_grease": True,
    "flammable": True,
    "combustion_products": "Water, carbon oxides",
}

# --- Specimen Printing Conditions (used for the property tests above) ---
SPECIMEN_TEST = {
    "nozzle_temp_c": 220,
    "bed_temp_c": 35,
    "printing_speed_mm_s": 200,
    "infill_density_pct": 100,
    "note": "Specimens annealed and dried at 55 C for 8 h before testing.",
}

# --- SI convenience fields for FEM (matches sim_struct/structural.py) ---
DENSITY_KG_M3 = 1240.0                  # 1.24 g/cm3
YOUNGS_MODULUS_PA = 2.58e9              # X-Y, 2580 MPa
POISSON_RATIO = 0.35                   # NOT in datasheet; typical PLA value
