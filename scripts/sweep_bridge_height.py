import subprocess
import json
import os

def sweep_bridge_height():
    print("Starting bridge height sweep...")
    heights = [20.0, 25.0, 30.0, 35.0, 40.0]
    results = []

    for height in heights:
        print(f"Running CAD generation with bridge_height={height}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_height", str(height)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((height, mass))
            print(f"Height: {height} mm -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for height, mass in results:
        print(f"bridge_height={height}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_height()
