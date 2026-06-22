import subprocess
import json

def sweep_f_hole_profile():
    print("Starting f_hole_profile sweep...")
    values = ['slot', 'classic']
    results = []

    for val in values:
        print(f"Running CAD generation with f_hole_profile={val}")
        subprocess.run(["python3", "cad/violin.py", "--f_hole_profile", val], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("top_mass_g", 0.0)
            results.append((val, mass))
            print(f"f_hole_profile: {val} -> Mass: {mass:.2f} g")

    print("\nSweep Complete. Results:")
    for val, mass in results:
        print(f"f_hole_profile={val}: mass={mass:.2f}")

    return results

if __name__ == "__main__":
    sweep_f_hole_profile()
