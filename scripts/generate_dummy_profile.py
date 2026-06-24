import os
import json

def generate_dummy_profiles(output_dir="profiles"):
    """
    Generate dummy JSON profiles for Orca Slicer.
    Creates machine.json, process.json, and filament.json in the specified directory.
    """
    os.makedirs(output_dir, exist_ok=True)

    machine_profile = {
        "type": "machine",
        "setting_id": "Bambu Lab X1 Carbon 0.4 nozzle",
        "name": "Bambu Lab X1 Carbon 0.4 nozzle",
        "from": "system",
        "instantiation": "true",
        "printer_technology": "FFF",
        "printer_model": "Bambu Lab X1 Carbon",
        "nozzle_diameter": [
            "0.4"
        ],
        "printable_area": [
            "0x0",
            "600x0",
            "600x600",
            "0x600"
        ],
        "printable_height": "600",
        "layer_change_gcode": "; layer change\nG92 E0"
    }

    process_profile = {
        "type": "process",
        "setting_id": "0.20mm Standard @BBL X1C",
        "name": "0.20mm Standard @BBL X1C",
        "from": "system",
        "instantiation": "true",
        "layer_height": "0.2",
        "initial_layer_height": "0.2",
        "line_width": "0.42",
        "initial_layer_line_width": "0.5",
        "outer_wall_line_width": "0.42",
        "inner_wall_line_width": "0.45",
        "sparse_infill_line_width": "0.45",
        "solid_infill_line_width": "0.42",
        "top_surface_line_width": "0.42",
        "wall_loops": "2",
        "top_shell_layers": "4",
        "bottom_shell_layers": "3",
        "sparse_infill_density": "15%",
        "sparse_infill_pattern": "grid",
        "default_print_speed": "200",
        "outer_wall_speed": "200",
        "inner_wall_speed": "300",
        "sparse_infill_speed": "270",
        "solid_infill_speed": "250",
        "top_surface_speed": "200",
        "travel_speed": "500",
        "compatible_printers": [
            "Bambu Lab X1 Carbon 0.4 nozzle"
        ]
    }

    filament_profile = {
        "type": "filament",
        "setting_id": "Bambu PLA Basic @BBL X1C",
        "name": "Bambu PLA Basic @BBL X1C",
        "from": "system",
        "instantiation": "true",
        "filament_type": [
            "PLA"
        ],
        "filament_diameter": [
            "1.75"
        ],
        "filament_density": [
            "1.24"
        ],
        "filament_cost": [
            "24.99"
        ],
        "nozzle_temperature": [
            "220"
        ],
        "nozzle_temperature_initial_layer": [
            "220"
        ],
        "hot_plate_temp": [
            "55"
        ],
        "hot_plate_temp_initial_layer": [
            "55"
        ],
        "compatible_printers": [
            "Bambu Lab X1 Carbon 0.4 nozzle"
        ]
    }

    files_to_create = {
        "machine.json": machine_profile,
        "process.json": process_profile,
        "filament.json": filament_profile
    }

    for filename, profile in files_to_create.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(profile, f, indent=4)

    print(f"Dummy profiles generated in '{output_dir}'")

if __name__ == "__main__":
    generate_dummy_profiles()
