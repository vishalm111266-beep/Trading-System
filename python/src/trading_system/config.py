from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
PINE_DIR = PROJECT_ROOT / "pine"
PYTHON_DIR = PROJECT_ROOT / "python"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TESTS_DIR = PROJECT_ROOT / "tests"

LOGGING_CONFIG = CONFIG_DIR / "logging.yaml"
