import subprocess
from sweep_tailpiece_y_offset import sweep_tailpiece_y_offset

def test_sweep_tailpiece_y_offset(monkeypatch):
    calls = []

    def mock_run(cmd, check, capture_output):
        if cmd[0] == "python3" and cmd[1] == "cad/violin.py":
            calls.append(cmd)
            # Create a mock json
            with open("violin_body.json", "w") as f:
                f.write('{"tailpiece_mass_g": 900.0}')
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)

    results = sweep_tailpiece_y_offset()

    assert len(results) == 5
    assert len(calls) == 5
    assert calls[0] == ["python3", "cad/violin.py", "--tailpiece_y_offset", "10.0"]
