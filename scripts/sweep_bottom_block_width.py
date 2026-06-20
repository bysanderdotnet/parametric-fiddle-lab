import subprocess
import json
import os

def sweep_bottom_block_width():
    print("Starting bottom block width sweep...")
    widths = [20.0, 30.0, 40.0, 50.0]
    results = []

    for width in widths:
        print(f"Running CAD generation with bottom_block_width={width}")
        subprocess.run(["python3", "cad/violin.py", "--bottom_block_width", str(width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bottom_block_mass_g", 0.0)
            results.append((width, mass))
            print(f"Width: {width} mm -> Bottom Block Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for width, mass in results:
        print(f"bottom_block_width={width}: bottom_block_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bottom_block_width()
