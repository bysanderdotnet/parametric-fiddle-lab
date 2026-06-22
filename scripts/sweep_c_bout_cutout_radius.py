import subprocess
import json

def sweep_c_bout_cutout_radius():
    print("Starting c_bout_cutout_radius sweep...")
    values = [30.00, 37.50, 45.00, 52.50, 60.00]
    results = []

    for val in values:
        print(f"Running CAD generation with c_bout_cutout_radius={val}")
        subprocess.run(["python3", "cad/violin.py", "--c_bout_cutout_radius", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"c_bout_cutout_radius: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"c_bout_cutout_radius={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_c_bout_cutout_radius()
