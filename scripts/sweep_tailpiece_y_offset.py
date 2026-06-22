import subprocess
import json

def sweep_tailpiece_y_offset():
    print("Starting tailpiece y offset sweep...")
    vals = [10.0, 15.0, 20.0, 25.0, 30.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with tailpiece_y_offset={val}")
        subprocess.run(["python3", "cad/violin.py", "--tailpiece_y_offset", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("tailpiece_mass_g", 0.0)
            results.append((val, mass))
            print(f"tailpiece_y_offset: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"tailpiece_y_offset={val}: tailpiece_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_tailpiece_y_offset()
