import subprocess
import json
import os

def sweep_soundpost_thickness():
    print("Starting soundpost thickness sweep...")
    thicknesses = [4.0, 5.0, 6.0, 7.0, 8.0]
    results = []

    for thickness in thicknesses:
        print(f"Running CAD generation with soundpost_thickness={thickness}")
        subprocess.run(["python3", "cad/violin.py", "--soundpost_thickness", str(thickness)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("soundpost_mass_g", 0.0)
            results.append((thickness, mass))
            print(f"Thickness: {thickness} mm -> Soundpost Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for thickness, mass in results:
        print(f"soundpost_thickness={thickness}: soundpost_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_soundpost_thickness()
