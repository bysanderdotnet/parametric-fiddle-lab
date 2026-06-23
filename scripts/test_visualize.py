import sys
import subprocess
import os
import cadquery as cq

def test_visualize():
    # Make some dummy step files
    cube1 = cq.Workplane("XY").box(1, 1, 1)
    cube2 = cq.Workplane("XY").box(1.2, 1.2, 1.2)

    cq.exporters.export(cube1, "test_generated.step")
    cq.exporters.export(cube2, "test_reference.step")

    proc = None
    try:
        # Run it for 2 seconds just to ensure no immediate crash
        proc = subprocess.Popen([sys.executable, "scripts/visualize.py", "test_generated.step", "test_reference.step"])
        proc.communicate(timeout=2)

        # If it didn't timeout, it exited early, which means it crashed.
        # Check return code. If it's not 0, it definitely crashed.
        if proc.returncode is not None and proc.returncode != 0:
            assert False, f"visualize.py crashed with return code {proc.returncode}"
    except subprocess.TimeoutExpired:
        # Expected behavior: stays open
        proc.kill()
        assert True
    finally:
        if proc and proc.returncode is None:
            proc.kill()
        if os.path.exists("test_generated.step"):
            os.remove("test_generated.step")
        if os.path.exists("test_reference.step"):
            os.remove("test_reference.step")
