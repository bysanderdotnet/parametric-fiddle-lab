import subprocess
import json

def sweep_bass_bar_width():
    print("Starting bass bar width sweep...")
    widths = [4.0, 5.0, 6.0, 7.0, 8.0]
    results = []

    for width in widths:
        print(f"Running CAD generation with bass_bar_width={width}")
        subprocess.run(["python3", "cad/violin.py", "--bass_bar_width", str(width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bass_bar_mass_g", 0.0)
            results.append((width, mass))
            print(f"Bass Bar Width: {width} mm -> Bass Bar Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for width, mass in results:
        print(f"bass_bar_width={width}: bass_bar_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bass_bar_width()
