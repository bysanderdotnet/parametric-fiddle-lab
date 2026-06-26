import subprocess
import os
import logging
import tempfile
import shutil
import zipfile
import json
import threading

logger = logging.getLogger(__name__)

_PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles")

DEFAULT_PROFILES = {
    "machine": os.path.join(_PROFILES_DIR, "machine.json"),
    "process": os.path.join(_PROFILES_DIR, "process.json"),
    "filament": os.path.join(_PROFILES_DIR, "filament.json"),
}

def slice_model(stl_file: str, output_gcode: str, profile: str | dict | None = None, extra_args: list = None, debug: bool = False):
    if extra_args is None:
        extra_args = []

    if not os.path.exists(stl_file):
        raise FileNotFoundError(f"Input file not found: {stl_file}")

    stl_file_abs = os.path.abspath(stl_file)
    output_gcode_abs = os.path.abspath(output_gcode)

    tmpdir = tempfile.mkdtemp(prefix="orca_slice_")
    logger.info(f"Working directory created at: {tmpdir}")

    pipe_path = os.path.join(tmpdir, "progress.pipe")
    os.mkfifo(pipe_path)

    def read_pipe():
        with open(pipe_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    pct = data.get('total_percent', 0.0)
                    msg = data.get('message', '')
                    logger.info(f"Orca progress: {pct}% - {msg}")
                except json.JSONDecodeError:
                    pass

    pipe_thread = threading.Thread(target=read_pipe)
    pipe_thread.start()

    try:
        cmd = ["orca-slicer", "--slice", "1", "--export-3mf", "output.gcode.3mf"]
        cmd.extend(["--pipe", pipe_path])

        if profile is None:
            profile = DEFAULT_PROFILES

        if isinstance(profile, dict):
            settings_paths = []
            if 'machine' in profile and os.path.exists(profile['machine']):
                settings_paths.append(os.path.abspath(profile['machine']))
            if 'process' in profile and os.path.exists(profile['process']):
                settings_paths.append(os.path.abspath(profile['process']))

            if settings_paths:
                cmd.extend(["--load-settings", ";".join(settings_paths)])

            if 'filament' in profile and os.path.exists(profile['filament']):
                cmd.extend(["--load-filaments", os.path.abspath(profile['filament'])])
        else:
            logger.warning(f"Profile ({profile}) is a string and not currently mapped to orca-slicer CLI flags. Pass a dict with 'machine', 'process', 'filament' paths.")

        cmd = cmd + extra_args + [stl_file_abs]

        result = subprocess.run(cmd, cwd=tmpdir, check=True, capture_output=True, text=True)

        try:
            fd = os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, b'\n')
            os.close(fd)
        except OSError:
            pass
        pipe_thread.join()

        out_3mf = os.path.join(tmpdir, "output.gcode.3mf")
        if os.path.exists(out_3mf):
            with zipfile.ZipFile(out_3mf, 'r') as z:
                gcode_files = [f for f in z.namelist() if f.endswith('.gcode')]
                if gcode_files:
                    with z.open(gcode_files[0]) as zf, open(output_gcode_abs, 'wb') as f:
                        shutil.copyfileobj(zf, f)
                else:
                    logger.warning("No .gcode file found inside the generated .3mf archive.")

                if "Metadata/slice_info.config" in z.namelist():
                    slice_info_path = os.path.join(os.path.dirname(output_gcode_abs), "slice_info.config")
                    with z.open("Metadata/slice_info.config") as zf, open(slice_info_path, 'wb') as f:
                        shutil.copyfileobj(zf, f)
                else:
                    logger.warning("No Metadata/slice_info.config found inside the generated .3mf archive.")
        else:
            logger.warning("output.gcode.3mf was not generated.")

        slice_meta = _read_slice_info(os.path.join(os.path.dirname(output_gcode_abs), "slice_info.config"))
        return result.stdout, slice_meta
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Orca Slicer CLI error: {e.stderr}") from e
    except FileNotFoundError as e:
        raise RuntimeError("orca-slicer executable not found") from e
    finally:
        try:
            fd = os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, b'\n')
            os.close(fd)
        except OSError:
            pass
        if pipe_thread.is_alive():
            pipe_thread.join()

        if not debug:
            shutil.rmtree(tmpdir, ignore_errors=True)


def _read_slice_info(path):
    """Parse slice_info.config into a dict of standardised keys."""
    meta = {}
    if not os.path.exists(path):
        return meta
    try:
        with open(path, "r") as f:
            raw = f.read()
        raw = raw.strip()
        if raw.startswith("{"):
            data = json.loads(raw)
        else:
            return meta
        for key in ("weight", "volume", "filament_mm", "filament_g", "total_time_s", "total_cost"):
            val = data.get(key)
            if val is not None:
                meta[key] = float(val)
        meta["filament_used_g"] = data.get("filament_used_g") or data.get("filament_g", 0.0)
    except (json.JSONDecodeError, OSError):
        pass
    return meta


def read_slice_metadata(gcode_path):
    """Read the slice_info.config that was written alongside *gcode_path*."""
    base = os.path.dirname(gcode_path) if os.path.dirname(gcode_path) else "."
    slice_info_path = os.path.join(base, "slice_info.config")
    return _read_slice_info(slice_info_path)
