import subprocess
import json

def sweep_purfling_groove_offset():
    print("Starting purfling_groove_offset sweep...")
    values = [1.00, 1.75, 2.50, 3.25, 4.00]
    results = []

    for val in values:
        print(f"Running CAD generation with purfling_groove_offset={val}")
        subprocess.run(["python3", "cad/violin.py", "--purfling_groove_offset", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"purfling_groove_offset: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"purfling_groove_offset={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_purfling_groove_offset()
