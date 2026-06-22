import subprocess
import json

def sweep_peg_hole_radius():
    print("Starting peg_hole_radius sweep...")
    values = [2.50, 2.75, 3.00, 3.25, 3.50]
    results = []

    for val in values:
        print(f"Running CAD generation with peg_hole_radius={val}")
        subprocess.run(["python3", "cad/violin.py", "--peg_hole_radius", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"peg_hole_radius: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"peg_hole_radius={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_peg_hole_radius()
