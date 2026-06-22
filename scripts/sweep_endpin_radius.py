import subprocess
import json

def sweep_endpin_radius():
    print("Starting endpin_radius sweep...")
    values = [3.00, 3.75, 4.50, 5.25, 6.00]
    results = []

    for val in values:
        print(f"Running CAD generation with endpin_radius={val}")
        subprocess.run(["python3", "cad/violin.py", "--endpin_radius", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"endpin_radius: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"endpin_radius={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_endpin_radius()
