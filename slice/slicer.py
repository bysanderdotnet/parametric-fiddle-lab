import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def slice_model(stl_file: str, profile: str, output_gcode: str, extra_args: list = None):
    """
    Wrapper for Orca Slicer CLI.

    Args:
        stl_file: Path to the input 3D model (e.g., STL, 3MF).
        profile: Path to the configuration profile.
        output_gcode: Path where the resulting sliced file (e.g., gcode) should be saved.
        extra_args: A list of additional command-line arguments to pass to orca-slicer.
    """
    if extra_args is None:
        extra_args = []

    if not os.path.exists(stl_file):
        raise FileNotFoundError(f"Input file not found: {stl_file}")

    # Build the generic command line array
    cmd = ["orca-slicer"] + extra_args + [stl_file]

    logger.info(f"Using input file: {stl_file}")
    logger.warning(f"Profile ({profile}) and output path ({output_gcode}) are not currently mapped to orca-slicer CLI flags pending CLI documentation.")

    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Slicing completed successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Slicing failed with return code {e.returncode}.")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise RuntimeError(f"Orca Slicer CLI error: {e.stderr}") from e
    except FileNotFoundError as e:
        logger.error("orca-slicer command not found. Is it installed and in PATH?")
        raise RuntimeError("orca-slicer executable not found") from e
