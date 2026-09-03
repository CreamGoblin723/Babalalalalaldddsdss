"""Simple persisted options: master volume + fullscreen toggle."""
import json
import os

from game import constants as C

DEFAULT_SETTINGS = {
    "master_volume": 0.7,
    "fullscreen": False,
}


def load_settings() -> dict:
    if not os.path.exists(C.SETTINGS_PATH):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(C.SETTINGS_PATH, "r") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    os.makedirs(C.SAVES_DIR, exist_ok=True)
    with open(C.SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)
