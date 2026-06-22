import subprocess
import json

def sweep_fingerboard_width_bottom():
    print("Starting fingerboard_width_bottom sweep...")
    values = [40.00, 41.00, 42.00, 43.00, 44.00]
    results = []

    for val in values:
        print(f"Running CAD generation with fingerboard_width_bottom={val}")
        subprocess.run(["python3", "cad/violin.py", "--fingerboard_width_bottom", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"fingerboard_width_bottom: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"fingerboard_width_bottom={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_fingerboard_width_bottom()
