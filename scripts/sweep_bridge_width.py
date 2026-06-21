import subprocess
import json
import os

def sweep_bridge_width():
    print("Starting bridge width (bottom) sweep...")
    widths = [35.0, 37.5, 40.0, 42.5, 45.0]
    results = []

    for width in widths:
        print(f"Running CAD generation with bridge_width_bottom={width}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_width_bottom", str(width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((width, mass))
            print(f"Width (bottom): {width} mm -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for width, mass in results:
        print(f"bridge_width_bottom={width}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_width()
