import pytest
import subprocess
import os

from generate_slicing_table import generate_slicing_table

def test_generate_slicing_table():
    markdown = generate_slicing_table()

    # Check headers
    assert "| Profile | Layer Height (mm) | Infill Density (%) |" in markdown
    assert "|---|---|---|" in markdown

    # Check rows exist
    assert "| Fast | 0.28 | 15 |" in markdown
    assert "| Strong | 0.20 | 40 |" in markdown
    assert "| Quality | 0.12 | 20 |" in markdown
    assert "| Lightweight | 0.24 | 5 |" in markdown

def test_script_execution():
    script_path = os.path.join(os.path.dirname(__file__), 'generate_slicing_table.py')
    result = subprocess.run(['python3', script_path], capture_output=True, text=True, check=True)

    markdown = result.stdout
    assert "| Profile | Layer Height (mm) | Infill Density (%) |" in markdown
    assert "| Fast | 0.28 | 15 |" in markdown
