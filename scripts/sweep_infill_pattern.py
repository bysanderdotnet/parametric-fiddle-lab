import subprocess
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model

def sweep_infill_pattern():
    print("Starting infill_pattern sweep...")
    values = ["grid", "gyroid", "honeycomb", "rectilinear"]
    results = []

    print("Running CAD generation for base model")
    subprocess.run(["python3", "cad/violin.py"], check=True, capture_output=True)

    for val in values:
        print(f"Slicing with infill_pattern={val}")

        extra_args = ["--sparse-infill-pattern", val]

        try:
            dummy_profile = {
                "machine": "profiles/machine.json",
                "process": "profiles/process.json",
                "filament": "profiles/filament.json"
            }
            slice_model("violin_body.stl", "violin_body.gcode", dummy_profile, extra_args=extra_args)
            results.append((val, "Success"))
            print(f"infill_pattern: {val} -> Sliced successfully")
        except Exception as e:
            results.append((val, f"Failed: {e}"))
            print(f"infill_pattern: {val} -> Slicing failed")

    print("\nSweep Complete. Results:")
    for val, status in results:
        print(f"infill_pattern={val}: status={status}")

    return results

if __name__ == "__main__":
    sweep_infill_pattern()
