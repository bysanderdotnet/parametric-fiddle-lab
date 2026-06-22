import subprocess
import json

def sweep_length():
    print("Starting length sweep...")
    vals = [300.0, 325.0, 350.0, 375.0, 400.0]
    results = []

    for val in vals:
        print(f"Running CAD generation with length={val}")
        subprocess.run(["python3", "cad/violin.py", "--length", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("mass_g", 0.0)
            results.append((val, mass))
            print(f"Length: {val} mm -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"length={val}: mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_length()
