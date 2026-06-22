import subprocess
import json

def sweep_peg_head_thickness():
    print("Starting peg_head_thickness sweep...")
    values = [3.00, 4.75, 6.50, 8.25, 10.00]
    results = []

    for val in values:
        print(f"Running CAD generation with peg_head_thickness={val}")
        subprocess.run(["python3", "cad/violin.py", "--peg_head_thickness", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"peg_head_thickness: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"peg_head_thickness={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_peg_head_thickness()
