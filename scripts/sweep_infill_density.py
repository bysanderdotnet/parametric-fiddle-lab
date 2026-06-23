import subprocess
import os
import sys

# Add root directory to python path to import slice_model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model

def sweep_infill_density():
    print("Starting infill_density sweep...")
    values = [5.0, 28.75, 52.5, 76.25, 100.0]
    results = []

    # First generate the CAD model since slicing requires it
    print("Running CAD generation for base model")
    subprocess.run(["python3", "cad/violin.py"], check=True, capture_output=True)

    for val in values:
        print(f"Slicing with infill_density={val}")

        extra_args = ["--sparse-infill-density", f"{val}%"]

        try:
            dummy_profile = {
                "machine": "profiles/machine.json",
                "process": "profiles/process.json",
                "filament": "profiles/filament.json"
            }
            slice_model("violin_body.stl", dummy_profile, "violin_body.gcode", extra_args=extra_args)
            # We don't have a specific output to read right now (like mass), just verify it runs
            results.append((val, "Success"))
            print(f"infill_density: {val} -> Sliced successfully")
        except Exception as e:
            results.append((val, f"Failed: {e}"))
            print(f"infill_density: {val} -> Slicing failed")

    print("\nSweep Complete. Results:")
    for val, status in results:
        print(f"infill_density={val}: status={status}")

    return results

if __name__ == "__main__":
    sweep_infill_density()
