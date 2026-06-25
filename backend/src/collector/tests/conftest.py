import sys
from pathlib import Path

_src = Path(__file__).parent.parent.parent  # backend/src/
sys.path.insert(0, str(_src / "collector"))
sys.path.insert(0, str(_src / "layers/common/python"))
