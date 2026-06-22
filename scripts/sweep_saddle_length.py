import subprocess
import json

def sweep_saddle_length():
    print("Starting saddle_length sweep...")
    values = [3.00, 4.25, 5.50, 6.75, 8.00]
    results = []

    for val in values:
        print(f"Running CAD generation with saddle_length={val}")
        subprocess.run(["python3", "cad/violin.py", "--saddle_length", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"saddle_length: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"saddle_length={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_saddle_length()
