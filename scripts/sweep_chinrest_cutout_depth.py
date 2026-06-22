import subprocess
import json

def sweep_chinrest_cutout_depth():
    print("Starting chinrest_cutout_depth sweep...")
    values = [2.00, 4.00, 6.00, 8.00, 10.00]
    results = []

    for val in values:
        print(f"Running CAD generation with chinrest_cutout_depth={val}")
        subprocess.run(["python3", "cad/violin.py", "--chinrest_cutout_depth", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"chinrest_cutout_depth: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"chinrest_cutout_depth={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_chinrest_cutout_depth()
