import subprocess
import json

def sweep_purfling_groove_width():
    print("Starting purfling_groove_width sweep...")
    values = [0.50, 0.88, 1.25, 1.62, 2.00]
    results = []

    for val in values:
        print(f"Running CAD generation with purfling_groove_width={val}")
        subprocess.run(["python3", "cad/violin.py", "--purfling_groove_width", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"purfling_groove_width: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"purfling_groove_width={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_purfling_groove_width()
