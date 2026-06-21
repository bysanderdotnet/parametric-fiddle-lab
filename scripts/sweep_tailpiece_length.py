import subprocess
import json

def sweep_tailpiece_length():
    print("Starting tailpiece length sweep...")
    lengths = [100.0, 105.0, 110.0, 115.0, 120.0]
    results = []

    for length in lengths:
        print(f"Running CAD generation with tailpiece_length={length}")
        subprocess.run(["python3", "cad/violin.py", "--tailpiece_length", str(length)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("tailpiece_mass_g", 0.0)
            results.append((length, mass))
            print(f"Tailpiece Length: {length} mm -> Tailpiece Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for length, mass in results:
        print(f"tailpiece_length={length}: tailpiece_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_tailpiece_length()