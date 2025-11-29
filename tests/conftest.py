import os
import sys
from pathlib import Path


# Ensure src/ is on path for imports during tests
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if SRC.is_dir():
    sys.path.insert(0, str(SRC))
