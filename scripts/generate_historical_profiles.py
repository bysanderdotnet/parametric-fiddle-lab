import json
import sys
import os
import inspect

# Ensure we can import from common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.params import SPEC
from cad.violin import create_violin_body

def generate_historical_profiles():
    # Start with default parameters
    sig = inspect.signature(create_violin_body)
    baseline_params = {}
    for name, param in sig.parameters.items():
        if param.default is not inspect.Parameter.empty:
            baseline_params[name] = param.default

    # Fill in any missing default parameters from SPEC
    for name, kind, opt, _ in SPEC:
        if name not in baseline_params:
            if kind == 'float':
                baseline_params[name] = sum(opt) / 2.0  # Midpoint
            elif kind == 'str':
                baseline_params[name] = opt[0]
            elif kind == 'bool':
                baseline_params[name] = opt[0]

    profiles = {
        "Stradivarius": {
            "length": 355.5,
            "upper_bout": 168.0,
            "c_bout": 111.0,
            "lower_bout": 208.0,
            "rib_height": 30.5,
            "f_hole_length": 76.0,
            "top_arch_height": 15.5,
            "back_arch_height": 15.0,
            "f_hole_profile": "classic",
            "neck_length": 130.0,
        },
        "Guarneri": {
            "length": 354.0,
            "upper_bout": 167.0,
            "c_bout": 112.0,
            "lower_bout": 206.0,
            "rib_height": 31.0,
            "f_hole_length": 78.0,
            "top_arch_height": 16.0,
            "back_arch_height": 15.5,
            "f_hole_profile": "classic",
            "neck_length": 130.0,
        },
        "Amati": {
            "length": 352.0,
            "upper_bout": 165.0,
            "c_bout": 109.0,
            "lower_bout": 204.0,
            "rib_height": 30.0,
            "f_hole_length": 74.0,
            "top_arch_height": 18.0, # Amati had higher arching
            "back_arch_height": 17.5,
            "f_hole_profile": "classic",
            "neck_length": 130.0,
        }
    }

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Generate JSON for each profile
    all_params = {}
    for name, overrides in profiles.items():
        params = baseline_params.copy()
        params.update(overrides)
        all_params[name] = params

        output_path = os.path.join(base_dir, f"{name.lower()}.json")
        with open(output_path, 'w') as f:
            json.dump(params, f, indent=4)
        print(f"Generated {name} parameters to {output_path}")

    # Generate Comparison Markdown Report
    report_path = os.path.join(base_dir, "historical_comparison.md")

    # Collect properties that have overrides
    differing_keys = set()
    for overrides in profiles.values():
        differing_keys.update(overrides.keys())

    # Sort keys for consistent output
    sorted_keys = sorted(list(differing_keys))

    with open(report_path, 'w') as f:
        f.write("# Historical Violin Profiles Comparison\n\n")
        f.write("| Parameter | Baseline | Stradivarius | Guarneri | Amati |\n")
        f.write("| --- | --- | --- | --- | --- |\n")

        for key in sorted_keys:
            baseline_val = baseline_params.get(key, "N/A")
            strad_val = all_params["Stradivarius"].get(key, "N/A")
            guarneri_val = all_params["Guarneri"].get(key, "N/A")
            amati_val = all_params["Amati"].get(key, "N/A")

            f.write(f"| `{key}` | {baseline_val} | {strad_val} | {guarneri_val} | {amati_val} |\n")

    print(f"Generated comparison report to {report_path}")

if __name__ == "__main__":
    generate_historical_profiles()
