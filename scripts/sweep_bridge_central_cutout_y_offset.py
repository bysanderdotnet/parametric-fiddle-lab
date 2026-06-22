import subprocess
import json

def sweep_bridge_central_cutout_y_offset():
    print("Starting bridge_central_cutout_y_offset sweep...")
    values = [10.0, 13.75, 17.5, 21.25, 25.0]
    results = []

    for val in values:
        print(f"Running CAD generation with bridge_central_cutout_y_offset={val}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_central_cutout_y_offset", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"bridge_central_cutout_y_offset: {val} -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"bridge_central_cutout_y_offset={val}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_central_cutout_y_offset()
