import subprocess
import json

def sweep_bass_bar_length():
    print("Starting bass bar length sweep...")
    lengths = [150.0, 175.0, 200.0, 225.0, 250.0]
    results = []

    for length in lengths:
        print(f"Running CAD generation with bass_bar_length={length}")
        subprocess.run(["python3", "cad/violin.py", "--bass_bar_length", str(length)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bass_bar_mass_g", 0.0)
            results.append((length, mass))
            print(f"Bass Bar Length: {length} mm -> Bass Bar Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for length, mass in results:
        print(f"bass_bar_length={length}: bass_bar_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bass_bar_length()
