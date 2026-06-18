import os
import sys
import subprocess
import pytest
from violin import create_violin_body

def test_create_violin_body():
    # Call create_violin_body with default parameters
    result = create_violin_body()

    # Check that it returns a tuple of length 22 (the number of return values)
    assert isinstance(result, tuple)
    assert len(result) == 22

    # Check that the first element (the violin body) is not None
    assert result[0] is not None

def test_violin_cli():
    # Remove files if they exist to start fresh
    for file in ["violin_body.step", "violin_cavity.step", "violin_body.json"]:
        if os.path.exists(file):
            os.remove(file)

    # Run the script via command line
    result = subprocess.run([sys.executable, "cad/violin.py"], capture_output=True, text=True)

    # Check that the process executed successfully
    assert result.returncode == 0

    # Verify that the expected files were created
    assert os.path.exists("violin_body.step")
    assert os.path.exists("violin_cavity.step")
    assert os.path.exists("violin_body.json")

    # Clean up
    for file in ["violin_body.step", "violin_cavity.step", "violin_body.json"]:
        if os.path.exists(file):
            os.remove(file)
