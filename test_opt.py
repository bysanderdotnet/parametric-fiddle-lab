import subprocess
import os

print("Running optimize script directly...")
result = subprocess.run(["python3", "opt/optimize.py"], check=False)
print("Exit code:", result.returncode)
