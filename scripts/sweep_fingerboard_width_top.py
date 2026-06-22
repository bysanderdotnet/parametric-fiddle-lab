import subprocess
import json

def sweep_fingerboard_width_top():
    print("Starting fingerboard_width_top sweep...")
    values = [22.00, 23.00, 24.00, 25.00, 26.00]
    results = []

    for val in values:
        print(f"Running CAD generation with fingerboard_width_top={val}")
        subprocess.run(["python3", "cad/violin.py", "--fingerboard_width_top", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"fingerboard_width_top: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"fingerboard_width_top={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_fingerboard_width_top()
