import subprocess
from sweep_back_arch_height import sweep_back_arch_height

def test_sweep_back_arch_height(monkeypatch):
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

    results = sweep_back_arch_height()

    assert len(results) == 5
    assert len(calls) == 5
    assert calls[0] == ["python3", "cad/violin.py", "--back_arch_height", "10.0"]
