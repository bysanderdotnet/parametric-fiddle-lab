import subprocess
import json

def sweep_endpin_length():
    print("Starting endpin_length sweep...")
    values = [15.00, 17.50, 20.00, 22.50, 25.00]
    results = []

    for val in values:
        print(f"Running CAD generation with endpin_length={val}")
        subprocess.run(["python3", "cad/violin.py", "--endpin_length", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"endpin_length: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"endpin_length={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_endpin_length()
