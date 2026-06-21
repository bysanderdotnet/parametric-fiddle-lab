import subprocess
import json
import os

def sweep_bridge_angle():
    print("Starting bridge angle sweep...")
    angles = [-10.0, -5.0, 0.0, 5.0, 10.0]
    results = []

    for angle in angles:
        print(f"Running CAD generation with bridge_angle={angle}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_angle", str(angle)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((angle, mass))
            print(f"Angle: {angle} degrees -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for angle, mass in results:
        print(f"bridge_angle={angle}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_angle()
