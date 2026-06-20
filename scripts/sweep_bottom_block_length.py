import subprocess
import json
import os

def sweep_bottom_block_length():
    print("Starting bottom block length sweep...")
    lengths = [10.0, 15.0, 20.0, 25.0]
    results = []

    for length in lengths:
        print(f"Running CAD generation with bottom_block_length={length}")
        subprocess.run(["python3", "cad/violin.py", "--bottom_block_length", str(length)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bottom_block_mass_g", 0.0)
            results.append((length, mass))
            print(f"Length: {length} mm -> Bottom Block Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for length, mass in results:
        print(f"bottom_block_length={length}: bottom_block_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bottom_block_length()
