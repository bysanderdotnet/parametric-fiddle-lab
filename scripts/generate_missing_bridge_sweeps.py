import os
import sys

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.params import SPEC

missing_bridge_params = [
    'bridge_width_bottom', 'bridge_radius', 'bridge_inner_curve_radius',
    'bridge_side_cutout_radius', 'bridge_cutout_radius', 'bridge_cutout_y_offset',
    'bridge_central_cutout', 'bridge_central_cutout_radius', 'bridge_central_cutout_y_offset',
    'bridge_foot_length', 'bridge_foot_width', 'bridge_foot_cutout_width',
    'bridge_foot_cutout_height', 'bridge_cutouts', 'bridge_y_offset'
]

sweep_template_float = """import subprocess
import json

def sweep_{param_name}():
    print("Starting {param_name} sweep...")
    values = [{v1}, {v2}, {v3}, {v4}, {v5}]
    results = []

    for val in values:
        print(f"Running CAD generation with {param_name}={{val}}")
        subprocess.run(["python3", "cad/violin.py", "--{param_name}", str(val)], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"{param_name}: {{val}} -> Bridge Mass: {{mass:.2f}} g")

    print("\\nSweep Complete. Results:")
    for val, mass in results:
        print(f"{param_name}={{val}}: bridge_mass_g={{mass:.2f}}")

    return results

if __name__ == "__main__":
    sweep_{param_name}()
"""

test_template_float = """import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_{param_name}

@patch("subprocess.run")
def test_sweep_{param_name}(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{{"bridge_mass_g": 2.5}}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_{param_name}.sweep_{param_name}()

    assert mock_run.call_count == 5
    assert len(results) == 5

    for val, mass in results:
        assert mass == 2.5
        assert val in [{v1}, {v2}, {v3}, {v4}, {v5}]
"""

sweep_template_bool = """import subprocess
import json

def sweep_{param_name}():
    print("Starting {param_name} sweep...")
    values = [True, False]
    results = []

    for val in values:
        print(f"Running CAD generation with {param_name}={{val}}")
        flag = f"--{param_name}" if val else f"--no-{param_name}"
        subprocess.run(["python3", "cad/violin.py", flag], check=True, capture_output=True)

        with open("violin_body.json", "r") as f:
            data = json.load(f)
            mass = data.get("bridge_mass_g", 0.0)
            results.append((val, mass))
            print(f"{param_name}: {{val}} -> Bridge Mass: {{mass:.2f}} g")

    print("\\nSweep Complete. Results:")
    for val, mass in results:
        print(f"{param_name}={{val}}: bridge_mass_g={{mass:.2f}}")

    return results

if __name__ == "__main__":
    sweep_{param_name}()
"""

test_template_bool = """import subprocess
import pytest
from unittest.mock import patch, mock_open

import sweep_{param_name}

@patch("subprocess.run")
def test_sweep_{param_name}(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    mock_json_content = '{{"bridge_mass_g": 2.5}}'

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        results = sweep_{param_name}.sweep_{param_name}()

    assert mock_run.call_count == 2
    assert len(results) == 2

    for val, mass in results:
        assert mass == 2.5
        assert val in [True, False]
"""

for param, ptype, opts, help_text in SPEC:
    if param in missing_bridge_params:
        if ptype == "float":
            v_min, v_max = opts
            step = (v_max - v_min) / 4
            v1, v2, v3, v4, v5 = v_min, v_min + step, v_min + 2*step, v_min + 3*step, v_max

            sweep_content = sweep_template_float.format(param_name=param, v1=v1, v2=v2, v3=v3, v4=v4, v5=v5)
            test_content = test_template_float.format(param_name=param, v1=v1, v2=v2, v3=v3, v4=v4, v5=v5)

        elif ptype == "bool":
            sweep_content = sweep_template_bool.format(param_name=param)
            test_content = test_template_bool.format(param_name=param)

        else:
            print(f"Skipping {param} due to unhandled type {ptype}")
            continue

        # Write sweep script
        with open(f"scripts/sweep_{param}.py", "w") as f:
            f.write(sweep_content)

        # Write test script
        with open(f"scripts/test_sweep_{param}.py", "w") as f:
            f.write(test_content)

        print(f"Generated scripts/sweep_{param}.py and scripts/test_sweep_{param}.py")
