import json
import sys
import os

# Ensure we can import from common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.params import SPEC

def generate_stradivarius_parameters():
    # Start with default parameters (using the mid-point of the bounds, or default lists)
    # The default params used in cad/violin.py create_violin_body signature are a good starting point,
    # but since we want defaults, we'll try to extract them from cad/violin.py directly.
    import inspect
    from cad.violin import create_violin_body

    sig = inspect.signature(create_violin_body)
    params = {}
    for name, param in sig.parameters.items():
        if param.default is not inspect.Parameter.empty:
            params[name] = param.default

    # Fill in any missing default parameters from SPEC
    for name, kind, opt, _ in SPEC:
        if name not in params:
            if kind == 'float':
                params[name] = sum(opt) / 2.0  # Midpoint
            elif kind == 'str':
                params[name] = opt[0]
            elif kind == 'bool':
                params[name] = opt[0]

    # Stradivarius (e.g., 1715 "Titian" or similar "Golden Period" models) dimensions:
    # Typical dimensions for a Strad model:
    # Back length: ~355.5 mm
    # Upper bout width: ~168 mm
    # Middle bout (c-bout) width: ~111 mm
    # Lower bout width: ~208 mm
    # Stop length: ~195 mm (implies bridge placement / f-hole offset)
    # F-hole length: ~76 mm
    # Rib height (top to bottom): varies from ~30mm to ~32mm

    overrides = {
        "length": 355.5,
        "upper_bout": 168.0,
        "c_bout": 111.0,
        "lower_bout": 208.0,
        "rib_height": 30.5,
        "f_hole_length": 76.0,
        # Typical arching height for a Strad is relatively flat compared to Amati/Stainer, around 15-16mm
        "top_arch_height": 15.5,
        "back_arch_height": 15.0,
        # F-hole style
        "f_hole_profile": "classic",
        # Neck length (typical modern setup for a Strad body)
        "neck_length": 130.0,
    }

    params.update(overrides)

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'stradivarius.json'))

    with open(output_path, 'w') as f:
        json.dump(params, f, indent=4)

    print(f"Generated Stradivarius parameters to {output_path}")

if __name__ == "__main__":
    generate_stradivarius_parameters()
