# tests/conftest.py
import sys
from pathlib import Path

# Добавление корня проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))