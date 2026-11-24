import sys
import unittest
from pathlib import Path

# Add the python_calls_c directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_CALLS_C = PROJECT_ROOT / "python_calls_c"
sys.path.insert(0, str(PYTHON_CALLS_C))

import numeric_wrapper as numeric