import subprocess
import json

def sweep_pegbox_angle():
    print("Starting pegbox_angle sweep...")
    values = [0.00, 3.75, 7.50, 11.25, 15.00]
    results = []

    for val in values:
        print(f"Running CAD generation with pegbox_angle={val}")
        subprocess.run(["python3", "cad/violin.py", "--pegbox_angle", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"pegbox_angle: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"pegbox_angle={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_pegbox_angle()
