import subprocess
from sweep_rib_height import sweep_rib_height

def test_sweep_rib_height(monkeypatch):
    calls = []

    def mock_run(cmd, check, capture_output):
        if cmd[0] == "python3" and cmd[1] == "cad/violin.py":
            calls.append(cmd)
            # Create a mock json
            with open("violin_body.json", "w") as f:
                f.write('{"mass_g": 900.0}')
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)

    results = sweep_rib_height()

    assert len(results) == 5
    assert len(calls) == 5
    assert calls[0] == ["python3", "cad/violin.py", "--rib_height", "10.0"]
