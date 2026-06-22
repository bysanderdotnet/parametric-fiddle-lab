import subprocess
import json

def sweep_bridge_inner_curve_radius():
    print("Starting bridge_inner_curve_radius sweep...")
    values = [5.0, 7.5, 10.0, 12.5, 15.0]
    results = []

    for val in values:
        print(f"Running CAD generation with bridge_inner_curve_radius={val}")
        subprocess.run(["python3", "cad/violin.py", "--bridge_inner_curve_radius", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"bridge_inner_curve_radius: {val} -> Bridge Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"bridge_inner_curve_radius={val}: bridge_mass_g={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_bridge_inner_curve_radius()
