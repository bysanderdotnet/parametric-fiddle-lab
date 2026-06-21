import subprocess
import json

def sweep_tailpiece_width_bottom():
    print("Starting tailpiece bottom width sweep...")
    widths = [15.0, 20.0, 25.0, 30.0, 35.0]
    results = []

    for width in widths:
        print(f"Running CAD generation with tailpiece_width_bottom={width}")
        subprocess.run(["python3", "cad/violin.py", "--tailpiece_width_bottom", str(width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("tailpiece_mass_g", 0.0)
            results.append((width, mass))
            print(f"Tailpiece Bottom Width: {width} mm -> Tailpiece Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for width, mass in results:
        print(f"tailpiece_width_bottom={width}: tailpiece_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_tailpiece_width_bottom()
