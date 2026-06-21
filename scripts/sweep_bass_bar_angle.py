import subprocess
import json

def sweep_bass_bar_angle():
    print("Starting bass bar angle sweep...")
    angles = [-5.0, 0.0, 5.0, 10.0, 15.0]
    results = []

    for angle in angles:
        print(f"Running CAD generation with bass_bar_angle={angle}")
        subprocess.run(["python3", "cad/violin.py", "--bass_bar_angle", str(angle)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bass_bar_mass_g", 0.0)
            results.append((angle, mass))
            print(f"Bass Bar Angle: {angle} degrees -> Bass Bar Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for angle, mass in results:
        print(f"bass_bar_angle={angle}: bass_bar_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bass_bar_angle()
