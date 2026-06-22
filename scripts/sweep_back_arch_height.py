import subprocess
import json

def sweep_back_arch_height():
    print("Starting back arch height sweep...")
    vals = [10.0, 15.0, 20.0, 25.0, 30.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with back_arch_height={val}")
        subprocess.run(["python3", "cad/violin.py", "--back_arch_height", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("mass_g", 0.0)
            results.append((val, mass))
            print(f"back_arch_height: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"back_arch_height={val}: mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_back_arch_height()
