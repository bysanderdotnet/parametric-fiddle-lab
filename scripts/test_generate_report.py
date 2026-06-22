import os
import json
import pytest
from scripts.generate_report import generate_report

@pytest.fixture
def mock_pipeline_outputs(tmp_path, monkeypatch):
    """Sets up mock JSON files and changes working directory to tmp_path."""
    monkeypatch.chdir(tmp_path)

    # Mock violin_body.json
    body_data = {
        "mass_g": 400.0,
        "volume_mm3": 300000.0,
        "bridge_mass_g": 2.5,
        "soundpost_mass_g": 1.2
    }
    with open("violin_body.json", "w") as f:
        json.dump(body_data, f)

    # Mock structural_results.json
    struct_data = {
        "mass_g": 405.0, # Structural might have an updated mass
        "max_stress_mpa": 15.0,
        "eigenmodes": [
            {"mode": 1, "frequency_hz": 300.0, "description": "CBR-like"},
            {"mode": 2, "frequency_hz": 400.0, "description": "B1- like"},
        ]
    }
    with open("structural_results.json", "w") as f:
        json.dump(struct_data, f)

    # Mock acoustic_results.json
    acoustic_data = {
        "cavity_modes": [
            {"mode": 1, "frequency_hz": 290.0, "description": "A0-like Helmholtz"},
            {"mode": 2, "frequency_hz": 450.0, "description": "A1-like"},
        ]
    }
    with open("acoustic_results.json", "w") as f:
        json.dump(acoustic_data, f)

    return tmp_path

def test_generate_report_creates_file(mock_pipeline_outputs):
    """Tests that the report generation script successfully creates a file."""
    output_file = "test_report.md"
    generate_report(output_file)

    assert os.path.exists(output_file)

def test_generate_report_content(mock_pipeline_outputs):
    """Tests that the report correctly incorporates data from all JSON files."""
    output_file = "test_report.md"
    md_content = generate_report(output_file)

    # Check physical properties
    assert "Total Mass:** 405.00 g" in md_content
    assert "Bridge:** 2.50 g" in md_content
    assert "Soundpost:** 1.20 g" in md_content
    assert "Total Volume:** 300000.0 mm³" in md_content

    # Check structural modes
    assert "Mode 1 (CBR-like):** 300.0 Hz" in md_content
    assert "Mode 2 (B1- like):** 400.0 Hz" in md_content

    # Check acoustic modes
    assert "Mode 1 (A0-like Helmholtz):** 290.0 Hz" in md_content
    assert "Mode 2 (A1-like):** 450.0 Hz" in md_content

def test_generate_report_missing_files(tmp_path, monkeypatch):
    """Tests the report generator when no JSON files are present."""
    monkeypatch.chdir(tmp_path)
    output_file = "test_report.md"
    md_content = generate_report(output_file)

    assert "Total Mass:** N/A g" in md_content
    assert "Total Volume:** N/A mm³" in md_content
    assert "No structural modes found" in md_content
    assert "No acoustic modes found" in md_content
