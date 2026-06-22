import subprocess
import json

def sweep_rib_height():
    print("Starting rib height sweep...")
    vals = [10.0, 15.0, 20.0, 25.0, 30.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with rib_height={val}")
        subprocess.run(["python3", "cad/violin.py", "--rib_height", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("mass_g", 0.0)
            results.append((val, mass))
            print(f"rib_height: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"rib_height={val}: mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_rib_height()
