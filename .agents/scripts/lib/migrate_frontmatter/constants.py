import re
from pathlib import Path

TOML_FM_RE = re.compile(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*$", re.MULTILINE | re.DOTALL)
YAML_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
EXCLUDE_DIRS = {".git", "vendor", ".temp", "__pycache__", "node_modules", ".venv"}
TOML_STORAGE_DIR = ".meta/toml"
BACKUP_DIR = ".meta/backup"
BASELINE_MANIFEST_PATH = ".meta/baseline-manifest.json"
