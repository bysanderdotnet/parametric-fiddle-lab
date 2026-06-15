#!/usr/bin/env sh
set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MARKER_FILE="$SCRIPT_DIR/.deps_installed"

if [ -f "$MARKER_FILE" ]; then
  # We cannot use "exit 0" directly if sourced, but here it is executed.
  # So exit 0 is fine, but to avoid shell block, we will just use if-else.
  echo "Dependencies already installed. Skipping..."
else
  echo "Installing system dependencies..."

  sudo apt-get update
  sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    gmsh \
    libfuse2t64 \
    libwebkit2gtk-4.1-0 \
    libmspack0 \
    curl \
    wget

  echo "Installing Elmer (ElmerSolver/ElmerGrid) from elmer-csc PPA..."
  # add-apt-repository is unreliable here, so wire the PPA by hand: fetch the
  # PPA signing key over HTTPS, dearmor to a keyring, add the apt source.
  ELMER_KEY=1FE4A88ACFEE8388A409F23A89358ABF9FB7E178
  CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
  curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x${ELMER_KEY}" \
    | sudo gpg --dearmor -o /usr/share/keyrings/elmer-csc.gpg --yes
  sudo chmod 644 /usr/share/keyrings/elmer-csc.gpg
  echo "deb [signed-by=/usr/share/keyrings/elmer-csc.gpg] https://ppa.launchpadcontent.net/elmer-csc-ubuntu/elmer-csc-ppa/ubuntu ${CODENAME} main" \
    | sudo tee /etc/apt/sources.list.d/elmer-csc.list
  sudo apt-get update
  sudo apt-get install -y elmerfem-csc

  echo "Installing OrcaSlicer..."
  sudo wget -O /usr/local/bin/OrcaSlicer.AppImage https://github.com/OrcaSlicer/OrcaSlicer/releases/download/v2.3.2/OrcaSlicer_Linux_AppImage_Ubuntu2404_V2.3.2.AppImage
  sudo chmod +x /usr/local/bin/OrcaSlicer.AppImage
  sudo ln -sf /usr/local/bin/OrcaSlicer.AppImage /usr/local/bin/orcaslicer
  sudo ln -sf /usr/local/bin/OrcaSlicer.AppImage /usr/local/bin/orca-slicer

  touch "$MARKER_FILE"
  echo "System dependencies installed successfully."
fi
