import subprocess
import json

def sweep_nut_height():
    print("Starting nut_height sweep...")
    values = [5.00, 6.25, 7.50, 8.75, 10.00]
    results = []

    for val in values:
        print(f"Running CAD generation with nut_height={val}")
        subprocess.run(["python3", "cad/violin.py", "--nut_height", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"nut_height: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"nut_height={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_nut_height()
