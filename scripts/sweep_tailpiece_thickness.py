import subprocess
import json

def sweep_tailpiece_thickness():
    print("Starting tailpiece thickness sweep...")
    thicknesses = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    results = []

    for thickness in thicknesses:
        print(f"Running CAD generation with tailpiece_thickness={thickness}")
        subprocess.run(["python3", "cad/violin.py", "--tailpiece_thickness", str(thickness)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("tailpiece_mass_g", 0.0)
            results.append((thickness, mass))
            print(f"Tailpiece Thickness: {thickness} mm -> Tailpiece Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for thickness, mass in results:
        print(f"tailpiece_thickness={thickness}: tailpiece_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_tailpiece_thickness()
