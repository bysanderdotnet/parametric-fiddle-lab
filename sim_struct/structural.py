import json
import random

def run_structural_sim(mesh_file):
    """Placeholder for Elmer/Code_Aster structural simulation."""
    print(f"Running placeholder structural simulation on {mesh_file}...")

    # Dummy results: eigenfrequencies (e.g. A0, C0, B1- like modes for a violin body)
    dummy_results = {
        "eigenmodes": [
            {"mode": 1, "frequency_hz": 280.0 + random.uniform(-10, 10), "description": "CBR-like"},
            {"mode": 2, "frequency_hz": 400.0 + random.uniform(-15, 15), "description": "B1- like"},
            {"mode": 3, "frequency_hz": 530.0 + random.uniform(-20, 20), "description": "B1+ like"}
        ],
        "max_stress_mpa": 15.4,
        "mass_g": 380.0
    }

    # Output to a dummy result file
    result_file = "structural_results.json"
    with open(result_file, "w") as f:
        json.dump(dummy_results, f, indent=4)

    print(f"Simulation complete. Results saved to {result_file}")
    return dummy_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run structural simulation.")
    parser.add_argument("--mesh", type=str, default="dummy.msh", help="Mesh file to simulate")
    args = parser.parse_args()

    run_structural_sim(args.mesh)
