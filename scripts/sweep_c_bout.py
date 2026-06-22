import subprocess
import json

def sweep_c_bout():
    print("Starting c bout sweep...")
    vals = [90.0, 100.0, 110.0, 120.0, 130.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with c_bout={val}")
        subprocess.run(["python3", "cad/violin.py", "--c_bout", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("mass_g", 0.0)
            results.append((val, mass))
            print(f"C Bout: {val} mm -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"c_bout={val}: mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_c_bout()
