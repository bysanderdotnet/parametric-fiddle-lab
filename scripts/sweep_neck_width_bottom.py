import subprocess
import json
import os

def sweep_neck_width_bottom():
    print("Starting neck width bottom sweep...")
    widths = [30.0, 32.0, 34.0, 36.0, 38.0]
    results = []

    for width in widths:
        print(f"Running CAD generation with neck_width_bottom={width}")
        subprocess.run(["python3", "cad/violin.py", "--neck_width_bottom", str(width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("neck_mass_g", 0.0)
            results.append((width, mass))
            print(f"Width bottom: {width} mm -> Neck Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for width, mass in results:
        print(f"neck_width_bottom={width}: neck_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_neck_width_bottom()
