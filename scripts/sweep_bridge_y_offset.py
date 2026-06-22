import subprocess
import json

def sweep_bridge_y_offset():
    print("Starting bridge_y_offset sweep...")
    values = [-20.0, -10.0, 0.0, 10.0, 20.0]
    results = []

    for val in values:
        print(f"Running CAD generation with bridge_y_offset={val}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_y_offset", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"bridge_y_offset: {val} -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"bridge_y_offset={val}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_y_offset()
