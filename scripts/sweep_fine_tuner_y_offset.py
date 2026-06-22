import subprocess
import json

def sweep_fine_tuner_y_offset():
    print("Starting fine_tuner_y_offset sweep...")
    values = [-10.00, -5.00, 0.00, 5.00, 10.00]
    results = []

    for val in values:
        print(f"Running CAD generation with fine_tuner_y_offset={val}")
        subprocess.run(["python3", "cad/violin.py", "--fine_tuner_y_offset", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"fine_tuner_y_offset: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"fine_tuner_y_offset={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_fine_tuner_y_offset()
