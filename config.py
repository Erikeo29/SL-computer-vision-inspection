"""Configuration globale de l'application -- AI Visual Inspection."""
import os

import yaml

# --- Chemins ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.join(ROOT_DIR, "docs")
DATA_PATH = os.path.join(ROOT_DIR, "data")
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")
CSS_PATH = os.path.join(ASSETS_PATH, "style.css")
MODELS_PATH = os.path.join(ROOT_DIR, "models")
SAMPLE_IMAGES_PATH = os.path.join(DATA_PATH, "sample_images")
LOG_PATH = os.path.join(DATA_PATH, "inspection_log.csv")

# --- Version ---
VERSION = "2.0.0"
VERSION_DATE = "Mar 2026"


def load_app_config() -> dict:
    """Charge la configuration YAML de l'application.

    Returns
    -------
    dict
        Configuration chargee depuis config.yaml.
    """
    config_path = os.path.join(ROOT_DIR, "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
