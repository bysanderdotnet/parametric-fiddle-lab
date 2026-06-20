import subprocess
import json
import os

def sweep_rib_thickness():
    print("Starting rib thickness sweep...")
    thicknesses = [2.0, 3.0, 4.0, 5.0, 6.0]
    results = []

    for thickness in thicknesses:
        print(f"Running CAD, meshing, and structural simulation with rib_thickness={thickness}")
        subprocess.run(["python3", "cad/violin.py", "--rib_thickness", str(thickness)], check=True, capture_output=True)
        subprocess.run(["python3", "mesh/mesher.py"], check=True, capture_output=True)
        subprocess.run(["python3", "sim_struct/structural.py"], check=True, capture_output=True)

        with open("structural_results.json", "r") as f:
            data = json.load(f)
            modes = data.get("eigenmodes", [])
            b1_minus_freq = None
            for mode in modes:
                if "B1-" in mode.get("description", ""):
                    b1_minus_freq = mode.get("frequency_hz")
                    break

            # fallback
            if b1_minus_freq is None and len(modes) > 1:
                b1_minus_freq = modes[1].get("frequency_hz")

            results.append((thickness, b1_minus_freq))
            freq_str = f"{b1_minus_freq:.1f} Hz" if b1_minus_freq else "Not found"
            print(f"rib_thickness: {thickness} mm -> B1- Frequency: {freq_str}")

    print("\nSweep Complete. Results:")
    for thickness, freq in results:
        freq_str = f"{freq:.1f} Hz" if freq else "Not found"
        print(f"rib_thickness={thickness}: B1-={freq_str}")

    return results

if __name__ == "__main__":
    sweep_rib_thickness()
