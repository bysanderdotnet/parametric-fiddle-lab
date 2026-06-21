import subprocess
import json

def sweep_tailpiece_width_top():
    print("Starting tailpiece top width sweep...")
    widths = [35.0, 40.0, 45.0, 50.0, 55.0]
    results = []

    for width in widths:
        print(f"Running CAD generation with tailpiece_width_top={width}")
        subprocess.run(["python3", "cad/violin.py", "--tailpiece_width_top", str(width)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("tailpiece_mass_g", 0.0)
            results.append((width, mass))
            print(f"Tailpiece Top Width: {width} mm -> Tailpiece Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for width, mass in results:
        print(f"tailpiece_width_top={width}: tailpiece_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_tailpiece_width_top()
