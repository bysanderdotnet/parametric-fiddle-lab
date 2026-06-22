import json
import os
import argparse

def generate_report(output_file="data/summary_report.md"):
    """Reads JSON results and generates a Markdown summary report."""
    # Ensure data directory exists if we're writing to it
    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # 1. Read violin_body.json
    body_data = {}
    try:
        with open("violin_body.json", "r") as f:
            body_data = json.load(f)
    except FileNotFoundError:
        print("Warning: violin_body.json not found")

    # 2. Read structural_results.json
    struct_data = {}
    try:
        with open("structural_results.json", "r") as f:
            struct_data = json.load(f)
    except FileNotFoundError:
        print("Warning: structural_results.json not found")

    # 3. Read acoustic_results.json
    acoustic_data = {}
    try:
        with open("acoustic_results.json", "r") as f:
            acoustic_data = json.load(f)
    except FileNotFoundError:
        print("Warning: acoustic_results.json not found")

    # Extract relevant fields
    mass_g = struct_data.get("mass_g", body_data.get("mass_g", "N/A"))
    volume_mm3 = body_data.get("volume_mm3", "N/A")

    # Format mass components
    mass_components = [
        f"  - **Total Mass:** {mass_g if isinstance(mass_g, str) else f'{mass_g:.2f}'} g",
    ]
    for key, val in body_data.items():
        if key.endswith("_mass_g") and key != "mass_g":
            name = key.replace("_mass_g", "").replace("_", " ").title()
            mass_components.append(f"  - **{name}:** {val:.2f} g")

    # Format structural modes
    struct_modes = []
    if "eigenmodes" in struct_data:
        for mode in struct_data["eigenmodes"]:
            freq = mode.get("frequency_hz", 0)
            desc = mode.get("description", "Unknown")
            struct_modes.append(f"  - **Mode {mode['mode']} ({desc}):** {freq:.1f} Hz")
    if not struct_modes:
        struct_modes.append("  - No structural modes found.")

    # Format acoustic modes
    ac_modes = []
    if "cavity_modes" in acoustic_data:
        for mode in acoustic_data["cavity_modes"]:
            freq = mode.get("frequency_hz", 0)
            desc = mode.get("description", "Unknown")
            ac_modes.append(f"  - **Mode {mode['mode']} ({desc}):** {freq:.1f} Hz")
    if not ac_modes:
        ac_modes.append("  - No acoustic modes found.")

    # Build the Markdown content
    md_content = f"""# Resonant Violin Lab: Optimization Summary Report

## 1. Physical Properties
{chr(10).join(mass_components)}
  - **Total Volume:** {volume_mm3 if isinstance(volume_mm3, str) else f'{volume_mm3:.1f}'} mm³

## 2. Structural Characteristics
{chr(10).join(struct_modes)}

## 3. Acoustic Characteristics
{chr(10).join(ac_modes)}
"""

    # Write to file
    with open(output_file, "w") as f:
        f.write(md_content)

    print(f"Report generated successfully at: {output_file}")
    return md_content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a markdown summary report from pipeline JSON outputs.")
    parser.add_argument("--output", type=str, default="data/summary_report.md", help="Path to output markdown file.")
    args = parser.parse_args()

    generate_report(args.output)
