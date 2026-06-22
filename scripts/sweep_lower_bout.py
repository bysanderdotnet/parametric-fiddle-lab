import subprocess
import json

def sweep_lower_bout():
    print("Starting lower bout sweep...")
    vals = [180.0, 192.5, 205.0, 217.5, 230.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with lower_bout={val}")
        subprocess.run(["python3", "cad/violin.py", "--lower_bout", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("mass_g", 0.0)
            results.append((val, mass))
            print(f"Lower Bout: {val} mm -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"lower_bout={val}: mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_lower_bout()
