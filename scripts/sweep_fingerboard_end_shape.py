import subprocess
import json

def sweep_fingerboard_end_shape():
    print("Starting fingerboard_end_shape sweep...")
    values = ['flat', 'curve']
    results = []

    for val in values:
        print(f"Running CAD generation with fingerboard_end_shape={val}")
        subprocess.run(["python3", "cad/violin.py", "--fingerboard_end_shape", val], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0)
            results.append((val, mass))
            print(f"fingerboard_end_shape: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"fingerboard_end_shape={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_fingerboard_end_shape()
