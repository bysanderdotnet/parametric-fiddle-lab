import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.generate_slicing_parameter_table import generate_slicing_parameter_table

def test_generate_slicing_parameter_table():
    with tempfile.TemporaryDirectory() as tempdir:
        output_file = os.path.join(tempdir, "slicing_parameters.md")
        md_content = generate_slicing_parameter_table(output_file)

        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        assert content == md_content
        assert "# Resonant Violin Lab Slicing Parameters" in content
        assert "| `infill_density` |" in content
        assert "| `layer_height` |" in content
        assert "| `bridge_width_top` |" not in content # Geometric parameter should not be in the table
