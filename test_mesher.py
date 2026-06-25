import subprocess

try:
    subprocess.run(["python3", "mesh/mesher.py"], check=True)
except subprocess.CalledProcessError:
    print("Meshing failed. Trying to fall back to default mesher...")
