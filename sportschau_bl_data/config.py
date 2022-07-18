from pathlib import Path

BASE_DIR = Path.home() / "project_data" / "sportschau_bl_data"
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DELAY = 2
