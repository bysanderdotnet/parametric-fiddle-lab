import subprocess
import json

def sweep_pegbox_depth():
    print("Starting pegbox_depth sweep...")
    values = [18.00, 19.00, 20.00, 21.00, 22.00]
    results = []

    for val in values:
        print(f"Running CAD generation with pegbox_depth={val}")
        subprocess.run(["python3", "cad/violin.py", "--pegbox_depth", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"pegbox_depth: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"pegbox_depth={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_pegbox_depth()
