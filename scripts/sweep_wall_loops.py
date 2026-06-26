import subprocess
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model

def sweep_wall_loops():
    print("Starting wall_loops sweep...")
    values = [1, 2, 3, 4, 5]
    results = []

    print("Running CAD generation for base model")
    subprocess.run(["python3", "cad/violin.py"], check=True, capture_output=True)

    for val in values:
        print(f"Slicing with wall_loops={val}")

        extra_args = ["--wall-loops", str(val)]

        try:
            dummy_profile = {
                "machine": "profiles/machine.json",
                "process": "profiles/process.json",
                "filament": "profiles/filament.json"
            }
            slice_model("violin_body.stl", "violin_body.gcode", dummy_profile, extra_args=extra_args)
            results.append((val, "Success"))
            print(f"wall_loops: {val} -> Sliced successfully")
        except Exception as e:
            results.append((val, f"Failed: {e}"))
            print(f"wall_loops: {val} -> Slicing failed")

    print("\nSweep Complete. Results:")
    for val, status in results:
        print(f"wall_loops={val}: status={status}")

    return results

if __name__ == "__main__":
    sweep_wall_loops()
