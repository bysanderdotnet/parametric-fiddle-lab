import subprocess
import json
import os

def sweep_bridge_mass():
    print("Starting bridge mass sweep...")
    thicknesses = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    results = []

    for thickness in thicknesses:
        print(f"Running CAD generation with bridge_thickness={thickness}")
        # Note: we set bridge_foot_width equal to thickness to avoid CAD boolean operation failures
        # when foot width is less than thickness but we aren't creating a foot base.
        foot_width = thickness
        subprocess.run(["python3", "cad/violin.py", "--bridge_thickness", str(thickness), "--bridge_foot_width", str(foot_width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((thickness, mass))
            print(f"Thickness: {thickness} mm -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for thickness, mass in results:
        print(f"bridge_thickness={thickness}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_mass()
