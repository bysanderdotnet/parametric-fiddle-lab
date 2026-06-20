import subprocess
import json
import os

def sweep_top_thickness():
    print("Starting top thickness sweep...")
    thicknesses = [2.0, 3.0, 4.0, 5.0, 6.0]
    results = []

    for thickness in thicknesses:
        print(f"Running CAD, meshing, and acoustic simulation with top_thickness={thickness}")
        subprocess.run(["python3", "cad/violin.py", "--top_thickness", str(thickness)], check=True, capture_output=True)
        subprocess.run(["python3", "mesh/mesher.py"], check=True, capture_output=True)
        subprocess.run(["python3", "sim_acoustic/acoustic.py"], check=True, capture_output=True)

        with open("acoustic_results.json", "r") as f:
            data = json.load(f)
            modes = data.get("cavity_modes", [])
            a0_freq = None
            for mode in modes:
                if "A0-like (Helmholtz)" in mode.get("description", ""):
                    a0_freq = mode.get("frequency_hz")
                    break

            # fallback
            if a0_freq is None and len(modes) > 0:
                a0_freq = modes[0].get("frequency_hz")

            results.append((thickness, a0_freq))
            freq_str = f"{a0_freq:.1f} Hz" if a0_freq else "Not found"
            print(f"top_thickness: {thickness} mm -> A0 Frequency: {freq_str}")

    print("\nSweep Complete. Results:")
    for thickness, freq in results:
        freq_str = f"{freq:.1f} Hz" if freq else "Not found"
        print(f"top_thickness={thickness}: A0={freq_str}")

    return results

if __name__ == "__main__":
    sweep_top_thickness()
