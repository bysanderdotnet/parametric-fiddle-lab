import subprocess
import json

def sweep_upper_bout():
    print("Starting upper bout sweep...")
    vals = [140.0, 152.5, 165.0, 177.5, 190.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with upper_bout={val}")
        subprocess.run(["python3", "cad/violin.py", "--upper_bout", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("mass_g", 0.0)
            results.append((val, mass))
            print(f"Upper Bout: {val} mm -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"upper_bout={val}: mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_upper_bout()
