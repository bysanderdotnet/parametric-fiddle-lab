import os
import tempfile
import subprocess
import math

def test_extract_resonant_frequencies():
    script_path = os.path.join(os.path.dirname(__file__), "extract_resonant_frequencies.sh")

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        log_file_path = f.name
        f.write("Some log output\n")
        f.write("EigenSolve:            1      1.000000000000000E+04\n")
        f.write("EigenSolve:            2      4.000000000000000E+04\n")
        f.write("EigenSolve:            3      0.000000000000000E+00\n")
        f.write("More log output\n")

    try:
        result = subprocess.run([script_path, log_file_path], capture_output=True, text=True, check=True)
        output = result.stdout

        freq1 = math.sqrt(10000.0) / (2 * math.pi)
        freq2 = math.sqrt(40000.0) / (2 * math.pi)

        assert f"{freq1:.2f}" in output
        assert f"{freq2:.2f}" in output
        assert "  3 |           0.00 | 0.000000e+00" in output

    finally:
        os.unlink(log_file_path)
