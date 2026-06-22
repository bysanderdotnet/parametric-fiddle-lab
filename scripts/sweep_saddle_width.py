import subprocess
import json

def sweep_saddle_width():
    print("Starting saddle_width sweep...")
    values = [25.00, 27.50, 30.00, 32.50, 35.00]
    results = []

    for val in values:
        print(f"Running CAD generation with saddle_width={val}")
        subprocess.run(["python3", "cad/violin.py", "--saddle_width", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"saddle_width: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"saddle_width={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_saddle_width()
