import subprocess
import json

def sweep_neck_angle():
    print("Starting neck angle sweep...")
    vals = [10.0, 15.0, 20.0, 25.0, 30.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with neck_angle={val}")
        subprocess.run(["python3", "cad/violin.py", "--neck_angle", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("neck_mass_g", 0.0)
            results.append((val, mass))
            print(f"neck_angle: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"neck_angle={val}: neck_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_neck_angle()
