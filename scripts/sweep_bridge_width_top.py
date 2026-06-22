import subprocess
import json

def sweep_bridge_width_top():
    print("Starting bridge width top sweep...")
    vals = [10.0, 15.0, 20.0, 25.0, 30.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with bridge_width_top={val}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_width_top", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"bridge_width_top: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"bridge_width_top={val}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_width_top()
