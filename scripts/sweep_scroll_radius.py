import subprocess
import json

def sweep_scroll_radius():
    print("Starting scroll_radius sweep...")
    values = [8.00, 9.00, 10.00, 11.00, 12.00]
    results = []

    for val in values:
        print(f"Running CAD generation with scroll_radius={val}")
        subprocess.run(["python3", "cad/violin.py", "--scroll_radius", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0) # Using top_mass_g as a general mass to track for missing params
            results.append((val, mass))
            print(f"scroll_radius: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"scroll_radius={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_scroll_radius()
