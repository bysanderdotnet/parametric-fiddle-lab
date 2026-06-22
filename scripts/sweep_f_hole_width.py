import subprocess
import json

def sweep_f_hole_width():
    print("Starting f_hole_width sweep...")
    values = [5.00, 6.75, 8.50, 10.25, 12.00]
    results = []

    for val in values:
        print(f"Running CAD generation with f_hole_width={val}")
        subprocess.run(["python3", "cad/violin.py", "--f_hole_width", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"f_hole_width: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"f_hole_width={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_f_hole_width()
