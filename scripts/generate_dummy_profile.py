import os
import json

def generate_dummy_profiles(output_dir="profiles"):
    """
    Generate dummy JSON profiles for Orca Slicer.
    Creates machine.json, process.json, and filament.json in the specified directory.
    """
    os.makedirs(output_dir, exist_ok=True)

    files_to_create = ["machine.json", "process.json", "filament.json"]

    for filename in files_to_create:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump({}, f)

    print(f"Dummy profiles generated in '{output_dir}'")

if __name__ == "__main__":
    generate_dummy_profiles()
