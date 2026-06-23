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
        "setting_id": "Default Printer",
        "name": "Default Printer",
        "from": "system",
        "instantiation": "true",
        "printer_technology": "FFF",
        "printer_model": "Generic",
        "printable_area": [
            "0x0",
            "600x0",
            "600x600",
            "0x600"
        ],
        "printable_height": "600",
        "layer_change_gcode": "G92 E0"
    }

    process_profile = {
        "type": "process",
        "setting_id": "Default Process",
        "name": "Default Process",
        "from": "system",
        "instantiation": "true",
        "layer_height": "0.2",
        "compatible_printers": ["Default Printer"]
    }

    filament_profile = {
        "type": "filament",
        "setting_id": "Default Filament",
        "name": "Default Filament",
        "from": "system",
        "instantiation": "true",
        "filament_diameter": ["1.75"],
        "compatible_printers": ["Default Printer"]
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
