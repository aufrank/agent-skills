import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "templates" / "config.json"


def resolve_config_path(config_path=None):
    if config_path:
        return Path(config_path)
    return DEFAULT_CONFIG_PATH


def load_config(config_path=None):
    path = resolve_config_path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path) as f:
        return json.load(f)
