import os
import pytest
from scripts.generate_parameter_table import generate_parameter_table
from common.params import SPEC

def test_generate_parameter_table_creates_file(tmp_path):
    output_file = tmp_path / "test_parameters.md"
    generate_parameter_table(str(output_file))

    assert os.path.exists(output_file)

def test_generate_parameter_table_content(tmp_path):
    output_file = tmp_path / "test_parameters.md"
    md_content = generate_parameter_table(str(output_file))

    # Check headers
    assert "| Parameter | Type | Range/Options | Description |" in md_content
    assert "|---|---|---|---|" in md_content

    # Check that some parameters from SPEC are present
    assert len(SPEC) > 0
    for name, kind, opt, help_text in SPEC[:5]: # just check first 5 to be sure
        assert f"`{name}`" in md_content
        assert f"`{kind}`" in md_content
        assert help_text in md_content

def test_generate_parameter_table_formatting(tmp_path):
    output_file = tmp_path / "test_parameters.md"
    md_content = generate_parameter_table(str(output_file))

    # Specifically test how a boolean or range might be formatted
    # We know bridge_central_cutout is a bool from our params exploration
    if any(s[0] == 'bridge_central_cutout' for s in SPEC):
        assert "True, False" in md_content

    # We know body_length is a float with range (340.0, 370.0)
    if any(s[0] == 'body_length' for s in SPEC):
        assert "[340.0, 370.0]" in md_content
