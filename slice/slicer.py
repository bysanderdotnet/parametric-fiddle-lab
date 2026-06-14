import subprocess
import os
import logging
import tempfile
import shutil
import zipfile

logger = logging.getLogger(__name__)

def slice_model(stl_file: str, profile: str | dict, output_gcode: str, extra_args: list = None, debug: bool = False):
    """
    Wrapper for Orca Slicer CLI.

    Args:
        stl_file: Path to the input 3D model (e.g., STL, 3MF).
        profile: Path to the configuration profile, or a dict containing 'machine', 'process', and 'filament' paths.
        output_gcode: Path where the resulting sliced file (e.g., gcode) should be saved.
        extra_args: A list of additional command-line arguments to pass to orca-slicer.
        debug: If True, the temporary working directory will not be deleted.
    """
    if extra_args is None:
        extra_args = []

    if not os.path.exists(stl_file):
        raise FileNotFoundError(f"Input file not found: {stl_file}")

    stl_file_abs = os.path.abspath(stl_file)
    output_gcode_abs = os.path.abspath(output_gcode)

    tmpdir = tempfile.mkdtemp(prefix="orca_slice_")
    logger.info(f"Working directory created at: {tmpdir}")

    try:
        # Build the generic command line array
        cmd = ["orca-slicer", "--slice", "1", "--export-3mf", "output.gcode.3mf"]

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

        logger.info(f"Using input file: {stl_file_abs}")

        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=tmpdir, check=True, capture_output=True, text=True)
        logger.info(f"Slicing completed successfully.")

        # Extract gcode from the resulting 3mf
        out_3mf = os.path.join(tmpdir, "output.gcode.3mf")
        if os.path.exists(out_3mf):
            with zipfile.ZipFile(out_3mf, 'r') as z:
                gcode_files = [f for f in z.namelist() if f.endswith('.gcode')]
                if gcode_files:
                    # Just take the first one
                    with z.open(gcode_files[0]) as zf, open(output_gcode_abs, 'wb') as f:
                        shutil.copyfileobj(zf, f)
                    logger.info(f"Extracted {gcode_files[0]} to {output_gcode_abs}")
                else:
                    logger.warning("No .gcode file found inside the generated .3mf archive.")
        else:
            logger.warning("output.gcode.3mf was not generated.")

        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Slicing failed with return code {e.returncode}.")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise RuntimeError(f"Orca Slicer CLI error: {e.stderr}") from e
    except FileNotFoundError as e:
        logger.error("orca-slicer command not found. Is it installed and in PATH?")
        raise RuntimeError("orca-slicer executable not found") from e
    finally:
        if not debug:
            shutil.rmtree(tmpdir, ignore_errors=True)
            logger.info(f"Cleaned up temporary directory {tmpdir}")
        else:
            logger.info(f"Debug mode enabled. Temporary directory left at: {tmpdir}")
