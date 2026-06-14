import subprocess
import os
import logging
import shutil

logger = logging.getLogger(__name__)

def slice_model(stl_file: str, profile: str, output_gcode: str, extra_args: list = None):
    """
    Wrapper for Orca Slicer CLI.

    Args:
        stl_file: Path to the input 3D model (e.g., STL, 3MF).
        profile: Path to the configuration profile.
        output_gcode: Path where the resulting sliced file (e.g., gcode) should be saved.
        extra_args: A list of additional command-line arguments to pass to orcaslicer.
    """
    if extra_args is None:
        extra_args = []

    if not os.path.exists(stl_file):
        raise FileNotFoundError(f"Input file not found: {stl_file}")

    # Temporary .3mf output
    temp_3mf = output_gcode + ".3mf"
    temp_extract_dir = output_gcode + "_extract"

    # Build the generic command line array
    cmd = ["orcaslicer"] + extra_args + ["--slice", "0", "--export-3mf", temp_3mf, stl_file]

    logger.info(f"Using input file: {stl_file}")
    logger.warning(f"Profile ({profile}) is not currently mapped to orcaslicer CLI flags pending CLI documentation.")

    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Slicing completed successfully.")

        # Extract the .gcode file from the .3mf archive
        logger.info(f"Extracting G-code from {temp_3mf} to {output_gcode}...")
        os.makedirs(temp_extract_dir, exist_ok=True)
        subprocess.run(["unzip", "-q", "-o", temp_3mf, "-d", temp_extract_dir], check=True)

        extracted_gcode = os.path.join(temp_extract_dir, "Metadata", "plate_1.gcode")
        if os.path.exists(extracted_gcode):
            shutil.copy2(extracted_gcode, output_gcode)
            logger.info(f"Successfully extracted G-code to {output_gcode}")
        else:
            logger.warning(f"Expected extracted G-code not found at {extracted_gcode}")

        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Slicing failed with return code {e.returncode}.")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise RuntimeError(f"Orca Slicer CLI error: {e.stderr}") from e
    except FileNotFoundError as e:
        if "orcaslicer" in str(e):
            logger.error("orcaslicer command not found. Is it installed and in PATH?")
            raise RuntimeError("orcaslicer executable not found") from e
        else:
            raise
    finally:
        # Cleanup temporary files
        if os.path.exists(temp_3mf):
            os.remove(temp_3mf)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
