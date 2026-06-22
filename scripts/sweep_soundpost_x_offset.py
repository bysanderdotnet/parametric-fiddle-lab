import subprocess
import json

def sweep_soundpost_x_offset():
    print("Starting soundpost_x_offset sweep...")
    values = [5.00, 10.00, 15.00, 20.00, 25.00]
    results = []

    for val in values:
        print(f"Running CAD generation with soundpost_x_offset={val}")
        subprocess.run(["python3", "cad/violin.py", "--soundpost_x_offset", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"soundpost_x_offset: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"soundpost_x_offset={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_soundpost_x_offset()
