import subprocess
import json
import os

def sweep_bridge_foot_height():
    print("Starting bridge foot height sweep...")
    heights = [3.0, 4.0, 5.0, 6.0, 7.0]
    results = []

    for height in heights:
        print(f"Running CAD generation with bridge_foot_height={height}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_foot_height", str(height)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((height, mass))
            print(f"Foot Height: {height} mm -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for height, mass in results:
        print(f"bridge_foot_height={height}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_foot_height()
