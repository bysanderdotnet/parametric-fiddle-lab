#!/bin/bash

# Check if a log file was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <elmer_log_file>"
    exit 1
fi

LOG_FILE="$1"

# Check if the file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: File '$LOG_FILE' not found."
    exit 1
fi

echo "Extracting resonant frequencies from '$LOG_FILE'..."
echo "Mode | Frequency (Hz) | Eigenvalue"
echo "-----------------------------------"

# Extract eigenvalues using awk, and calculate frequency
# Formula: frequency = sqrt(eigenvalue) / (2 * pi)
# pi ~ 3.141592653589793

awk '/EigenSolve:/ {
    if (NF >= 4) {
        val = $4
        # Ensure it is a number
        if (val ~ /^[+-]?[0-9]*(\.[0-9]+)?([eE][+-]?[0-9]+)?$/) {
            # Compute square root using awk math (sqrt)
            if (val > 0) {
                freq = sqrt(val) / (2 * 3.141592653589793)
                modes++
                printf "  %2d | %14.2f | %e\n", modes, freq, val
            } else if (val == 0) {
                freq = 0
                modes++
                printf "  %2d | %14.2f | %e\n", modes, freq, val
            }
        }
    }
}' "$LOG_FILE"
