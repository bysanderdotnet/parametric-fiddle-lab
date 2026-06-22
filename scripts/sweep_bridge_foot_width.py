import subprocess
import json

def sweep_bridge_foot_width():
    print("Starting bridge_foot_width sweep...")
    values = [3.0, 4.75, 6.5, 8.25, 10.0]
    results = []

    for val in values:
        print(f"Running CAD generation with bridge_foot_width={val}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_foot_width", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"bridge_foot_width: {val} -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"bridge_foot_width={val}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_foot_width()
