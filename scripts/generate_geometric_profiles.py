import json
import sys
import os
import inspect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.params import SPEC
from cad.violin import create_violin_body

PROFILES = {
    "Stradivarius (1715 Titian)": {
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
    "Guarneri del Gesu (1743 Il Cannone)": {
        "length": 354.0,
        "upper_bout": 168.0,
        "c_bout": 112.0,
        "lower_bout": 207.0,
        "rib_height": 31.0,
        "f_hole_length": 80.0,
        "top_arch_height": 16.0,
        "back_arch_height": 15.5,
        "f_hole_profile": "classic",
        "neck_length": 130.0,
    },
    "Amati (1666 Nicolo Amati)": {
        "length": 352.0,
        "upper_bout": 163.0,
        "c_bout": 109.0,
        "lower_bout": 202.0,
        "rib_height": 30.0,
        "f_hole_length": 72.0,
        "top_arch_height": 18.0,
        "back_arch_height": 18.0,
        "f_hole_profile": "classic",
        "neck_length": 130.0,
    }
}

def generate_profiles():
    sig = inspect.signature(create_violin_body)
    default_params = {}
    for name, param in sig.parameters.items():
        if param.default is not inspect.Parameter.empty:
            default_params[name] = param.default

    for name, kind, opt, _ in SPEC:
        if name not in default_params:
            if kind == 'float':
                default_params[name] = sum(opt) / 2.0
            elif kind == 'str':
                default_params[name] = opt[0]
            elif kind == 'bool':
                default_params[name] = opt[0]

    print("Parameter Comparison:")
    print(f"{'Parameter':<20} | {'Default':<10} | {'Stradivarius':<12} | {'Guarneri':<12} | {'Amati':<10}")
    print("-" * 73)

    compare_keys = ["length", "upper_bout", "c_bout", "lower_bout", "rib_height", "f_hole_length", "top_arch_height", "back_arch_height", "neck_length"]
    for key in compare_keys:
        def fmt(val):
            return f"{val:.1f}" if isinstance(val, (int, float)) else str(val)

        d_val = fmt(default_params.get(key, 'N/A'))
        s_val = fmt(PROFILES["Stradivarius (1715 Titian)"].get(key, 'N/A'))
        g_val = fmt(PROFILES["Guarneri del Gesu (1743 Il Cannone)"].get(key, 'N/A'))
        a_val = fmt(PROFILES["Amati (1666 Nicolo Amati)"].get(key, 'N/A'))

        print(f"{key:<20} | {d_val:<10} | {s_val:<12} | {g_val:<12} | {a_val:<10}")

    for profile_name, overrides in PROFILES.items():
        params = default_params.copy()
        params.update(overrides)

        filename = profile_name.split()[0].lower() + ".json"
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))

        with open(output_path, 'w') as f:
            json.dump(params, f, indent=4)
        print(f"\nGenerated {profile_name} parameters to {output_path}")

if __name__ == "__main__":
    generate_profiles()
