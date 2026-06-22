import subprocess
import json

def sweep_bridge_cutouts():
    print("Starting bridge_cutouts sweep...")
    values = [True, False]
    results = []

    for val in values:
        print(f"Running CAD generation with bridge_cutouts={val}")
        flag = f"--bridge_cutouts" if val else f"--no-bridge_cutouts"
        subprocess.run(["python3", "cad/violin.py", flag], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"bridge_cutouts: {val} -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"bridge_cutouts={val}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_cutouts()
