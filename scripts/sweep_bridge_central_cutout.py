import subprocess
import json

def sweep_bridge_central_cutout():
    print("Starting bridge_central_cutout sweep...")
    values = [True, False]
    results = []

    for val in values:
        print(f"Running CAD generation with bridge_central_cutout={val}")
        flag = f"--bridge_central_cutout" if val else f"--no-bridge_central_cutout"
        subprocess.run(["python3", "cad/violin.py", flag], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"bridge_central_cutout: {val} -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"bridge_central_cutout={val}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_central_cutout()
