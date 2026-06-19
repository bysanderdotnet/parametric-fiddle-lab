#!/bin/bash
source .venv/bin/activate
python3 -c "import sys; sys.path.append('opt'); from objective import evaluate_objective; print(evaluate_objective())"
