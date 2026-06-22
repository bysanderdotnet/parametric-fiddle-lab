import subprocess
from sweep_bridge_width_top import sweep_bridge_width_top

def test_sweep_bridge_width_top(monkeypatch):
    calls = []

    def mock_run(cmd, check, capture_output):
        if cmd[0] == "python3" and cmd[1] == "cad/violin.py":
            calls.append(cmd)
            # Create a mock json
            with open("violin_body.json", "w") as f:
                f.write('{"bridge_mass_g": 900.0}')
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_run)

    results = sweep_bridge_width_top()

    assert len(results) == 5
    assert len(calls) == 5
    assert calls[0] == ["python3", "cad/violin.py", "--bridge_width_top", "10.0"]
