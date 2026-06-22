import subprocess
import json

def sweep_top_arch_height():
    print("Starting top arch height sweep...")
    vals = [10.0, 13.75, 17.5, 21.25, 25.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with top_arch_height={val}")
        subprocess.run(["python3", "cad/violin.py", "--top_arch_height", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("mass_g", 0.0)
            results.append((val, mass))
            print(f"Top Arch Height: {val} mm -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"top_arch_height={val}: mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_top_arch_height()
