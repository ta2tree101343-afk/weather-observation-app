import os
import sys
from pathlib import Path

_backend = Path(__file__).parent
sys.path.insert(0, str(_backend / "src/layers/common/python"))
sys.path.insert(0, str(_backend / "src/api"))

os.environ.setdefault("TABLE_NAME", "test")
os.environ.setdefault("POWERTOOLS_TRACE_DISABLED", "true")
