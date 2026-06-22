import subprocess
import json

def sweep_fingerboard_thickness():
    print("Starting fingerboard_thickness sweep...")
    values = [4.00, 4.75, 5.50, 6.25, 7.00]
    results = []

    for val in values:
        print(f"Running CAD generation with fingerboard_thickness={val}")
        subprocess.run(["python3", "cad/violin.py", "--fingerboard_thickness", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"fingerboard_thickness: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"fingerboard_thickness={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_fingerboard_thickness()
