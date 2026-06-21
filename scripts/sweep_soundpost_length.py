import subprocess
import json
import os

def sweep_soundpost_length():
    print("Starting soundpost length sweep...")
    lengths = [45.0, 47.5, 50.0, 52.5, 55.0]
    results = []

    for length in lengths:
        print(f"Running CAD generation with soundpost_length={length}")
        subprocess.run(["python3", "cad/violin.py", "--soundpost_length", str(length)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("soundpost_mass_g", 0.0)
            results.append((length, mass))
            print(f"Soundpost Length: {length} mm -> Soundpost Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for length, mass in results:
        print(f"soundpost_length={length}: soundpost_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_soundpost_length()
