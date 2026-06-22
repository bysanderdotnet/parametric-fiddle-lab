import subprocess
import json
import os

def sweep_f_hole_x_offset():
    print("Starting f_hole_x_offset sweep...")
    values = [-20.0, -10.0, 0.0, 10.0, 20.0]
    results = []

    for val in values:
        print(f"Running CAD, meshing, and acoustic simulation with f_hole_x_offset={val}")
        subprocess.run(["python3", "cad/violin.py", f"--f_hole_x_offset", str(val)], check=True, capture_output=True)
        subprocess.run(["python3", "mesh/mesher.py"], check=True, capture_output=True)
        subprocess.run(["python3", "sim_acoustic/acoustic.py"], check=True, capture_output=True)

        with open("acoustic_results.json", "r") as f:
            data = json.load(f)
            modes = data.get("cavity_modes", [])
            a0_freq = None
            for mode in modes:
                if "A0" in mode.get("description", ""):
                    a0_freq = mode.get("frequency_hz")
                    break

            # fallback to the first mode if no A0 description
            if a0_freq is None and modes:
                a0_freq = modes[0].get("frequency_hz")

            results.append((val, a0_freq))
            freq_str = f"{a0_freq:.1f} Hz" if a0_freq else "Not found"
            print(f"f_hole_x_offset: {val} -> A0 Frequency: {freq_str}")

    print("\nSweep Complete. Results:")
    for val, freq in results:
        freq_str = f"{freq:.1f} Hz" if freq else "Not found"
        print(f"f_hole_x_offset={val}: A0={freq_str}")

    return results

if __name__ == "__main__":
    sweep_f_hole_x_offset()
