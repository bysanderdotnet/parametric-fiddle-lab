import subprocess
import json

def sweep_saddle_height():
    print("Starting saddle_height sweep...")
    values = [4.00, 5.00, 6.00, 7.00, 8.00]
    results = []

    for val in values:
        print(f"Running CAD generation with saddle_height={val}")
        subprocess.run(["python3", "cad/violin.py", "--saddle_height", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"saddle_height: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"saddle_height={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_saddle_height()
