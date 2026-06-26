import subprocess
import os
import sys

# Add root directory to python path to import slice_model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slice.slicer import slice_model

def sweep_layer_height():
    print("Starting layer_height sweep...")
    values = [0.08, 0.13, 0.18, 0.23, 0.28]
    results = []

    # First generate the CAD model since slicing requires it
    print("Running CAD generation for base model")
    subprocess.run(["python3", "cad/violin.py"], check=True, capture_output=True)

    for val in values:
        print(f"Slicing with layer_height={val}")

        extra_args = ["--layer-height", str(val)]

        try:
            dummy_profile = {
                "machine": "profiles/machine.json",
                "process": "profiles/process.json",
                "filament": "profiles/filament.json"
            }
            slice_model("violin_body.stl", "violin_body.gcode", dummy_profile, extra_args=extra_args)
            # We don't have a specific output to read right now (like mass), just verify it runs
            results.append((val, "Success"))
            print(f"layer_height: {val} -> Sliced successfully")
        except Exception as e:
            results.append((val, f"Failed: {e}"))
            print(f"layer_height: {val} -> Slicing failed")

    print("\nSweep Complete. Results:")
    for val, status in results:
        print(f"layer_height={val}: status={status}")

    return results

if __name__ == "__main__":
    sweep_layer_height()
