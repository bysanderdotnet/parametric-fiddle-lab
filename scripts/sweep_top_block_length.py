import subprocess
import json
import os

def sweep_top_block_length():
    print("Starting top block length sweep...")
    lengths = [10.0, 15.0, 20.0, 25.0]
    results = []

    for length in lengths:
        print(f"Running CAD generation with top_block_length={length}")
        subprocess.run(["python3", "cad/violin.py", "--top_block_length", str(length)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_block_mass_g", 0.0)
            results.append((length, mass))
            print(f"Length: {length} mm -> Top Block Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for length, mass in results:
        print(f"top_block_length={length}: top_block_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_top_block_length()
