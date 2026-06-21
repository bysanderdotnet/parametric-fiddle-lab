import subprocess
import json

def sweep_bass_bar_height():
    print("Starting bass bar height sweep...")
    heights = [5.0, 7.5, 10.0, 12.5, 15.0]
    results = []

    for height in heights:
        print(f"Running CAD generation with bass_bar_height={height}")
        subprocess.run(["python3", "cad/violin.py", "--bass_bar_height", str(height)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bass_bar_mass_g", 0.0)
            results.append((height, mass))
            print(f"Bass Bar Height: {height} mm -> Bass Bar Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for height, mass in results:
        print(f"bass_bar_height={height}: bass_bar_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bass_bar_height()