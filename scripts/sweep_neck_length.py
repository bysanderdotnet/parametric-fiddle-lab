import subprocess
import json
import os

def sweep_neck_length():
    print("Starting neck length sweep...")
    lengths = [110.0, 120.0, 130.0, 140.0, 150.0]
    results = []

    for length in lengths:
        print(f"Running CAD generation with neck_length={length}")
        subprocess.run(["python3", "cad/violin.py", "--neck_length", str(length)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("neck_mass_g", 0.0)
            results.append((length, mass))
            print(f"Length: {length} mm -> Neck Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for length, mass in results:
        print(f"neck_length={length}: neck_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_neck_length()
