import subprocess
import json
import os

def sweep_neck_width_top():
    print("Starting neck width top sweep...")
    widths = [20.0, 22.0, 24.0, 26.0, 28.0]
    results = []

    for width in widths:
        print(f"Running CAD generation with neck_width_top={width}")
        subprocess.run(["python3", "cad/violin.py", "--neck_width_top", str(width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("neck_mass_g", 0.0)
            results.append((width, mass))
            print(f"Width top: {width} mm -> Neck Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for width, mass in results:
        print(f"neck_width_top={width}: neck_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_neck_width_top()